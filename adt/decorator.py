# mypy: no-warn-unused-ignores
import sys
import inspect
from enum import Enum
from types import FrameType
from typing import Any, Callable, Type, TypeVar, no_type_check, Iterable, Optional

from adt.case import CaseConstructor


@no_type_check
def adt(cls):
    try:
        annotations = cls.__annotations__
    except AttributeError:
        # no annotations defined
        return cls

    caseConstructors = {
        k: constructor
        for k, constructor in annotations.items() if not k.startswith('__')
    }

    for k, constructor in caseConstructors.items():
        if not hasattr(constructor, 'constructCase'):
            raise TypeError(
                f'Annotation {k} should be a Case[…] constructor, got {constructor!r} instead'
            )

    cls._Key = Enum(  # type: ignore
        '_Key', list(caseConstructors.keys()))

    cls._types = list(x.getTypes() for x in list(caseConstructors.values()))

    caseKeys = cls._Key.__members__.values()
    _installInit(cls, caseKeys)
    _installRepr(cls)
    _installStr(cls)
    _installEq(cls)

    for caseKey in cls._Key.__members__.values():
        _installOneConstructor(cls, caseKey)

    _installMatch(cls, cls._Key)
    return cls


def _installInit(cls: Any, caseKeys: Iterable[Enum]) -> None:
    def _init(self: Any,
              key: Enum,
              value: Any,
              orig_init: Callable[[Any], None] = cls.__init__) -> None:
        self._key = key
        self._value = value

        for caseKey in caseKeys:
            _installOneAccessor(self, caseKey)

        orig_init(self)

    cls.__init__ = _init


def _installRepr(cls: Any) -> None:
    def _repr(self: Any) -> str:
        return f'{type(self)}.{self._key.name}({self._value})'

    if '__repr__' not in cls.__dict__:
        cls.__repr__ = _repr


def _installStr(cls: Any) -> None:
    def _str(self: Any) -> str:
        return f'<{type(self)}.{self._key.name}: {self._value}>'

    if '__str__' not in cls.__dict__:
        cls.__str__ = _str


def _installEq(cls: Any) -> None:
    # It's important to capture `cls` here, instead of using type(self), to
    # preserve covariance; i.e., if `self` and `other` are instances of
    # different descendants of `cls`, it's irrelevant for this particular
    # equality check and we shouldn't rule it out (that should be the job of
    # further-derived classes' implementation of __eq__).
    def _eq(self: Any, other: Any, cls: Type[Any] = cls) -> bool:
        if not isinstance(other, cls):
            return False

        return bool(self._key == other._key and self._value == other._value)

    if '__eq__' not in cls.__dict__:
        cls.__eq__ = _eq


def _installOneConstructor(cls: Any, case: Enum) -> None:
    def constructor(cls: Type[Any], *args: Any, _case: Enum = case) -> Any:
        return cls(key=_case,
                   value=cls.__annotations__[_case.name].constructCase(*args))

    if hasattr(cls, case.name):
        raise AttributeError(
            f'{cls} should not have a default value for {case.name}, as this will be a generated constructor'
        )

    setattr(cls, case.name, classmethod(constructor))


TraceFunction = Callable[[FrameType, str, Any], Any]


class Accessor:
    class SkipCase(Exception):
        pass

    def __init__(self, adt: Any, case: Enum):
        self.adt = adt
        self.case = case
        self.original_system_trace_function: Optional[TraceFunction] = None

    def __call__(self) -> Any:
        if self.adt._key != self.case:
            raise AttributeError(
                f'{self.adt} was constructed as case {self.adt._key.name}, so {self.case.name.lower()} is not accessible'
            )
        return self.adt._value

    def trace(self, frame: FrameType, event: str, arg: Any) -> Any:
        raise self.SkipCase()

    def __enter__(self) -> Any:
        if self.adt._key != self.case:
            self.original_system_trace_function = sys.gettrace()
            sys.settrace(lambda *args, **keys: None)
            frame = inspect.currentframe()
            if frame:
                setattr(frame.f_back, "f_trace", self.trace)
        else:
            return self.adt._value

    def __exit__(self, exc_type: type, exc_val: Exception,
                 exc_tb: Any) -> Optional[bool]:
        if self.SkipCase is exc_type:
            if self.original_system_trace_function:
                sys.settrace(self.original_system_trace_function)
                self.original_system_trace_function = None
            return True
        else:
            return None


def _installOneAccessor(instance: Any, case: Enum) -> None:
    accessorName = case.name.lower()
    if accessorName not in instance.__class__.__dict__:
        setattr(instance, accessorName, Accessor(instance, case))


_MatchResult = TypeVar('_MatchResult')


def _installMatch(cls: Any, cases: Type[Enum]) -> None:
    def match(self: Any,
              _cases: Type[Enum] = cases,
              **kwargs: Callable[..., _MatchResult]) -> _MatchResult:
        caseNames = _cases.__members__.keys()
        upperKeys = {k: k.upper() for k in kwargs.keys()}

        for key in upperKeys.values():
            if key not in caseNames:
                raise ValueError(
                    f'Unrecognized case {key} in pattern match against {self} (expected one of {caseNames})'
                )

        for key in caseNames:
            if key not in upperKeys.values():
                raise ValueError(
                    f'Incomplete pattern match against {self} (missing {key})')

        for key, callback in kwargs.items():
            upperKey = upperKeys[key]

            if self._key == _cases.__members__[upperKey]:
                caseConstructor: CaseConstructor.AnyConstructor = type(
                    self).__annotations__[upperKey]
                return caseConstructor.deconstructCase(self._value, callback)

        assert False, 'Execution should not reach here'

    if 'match' not in cls.__dict__:
        cls.match = match
