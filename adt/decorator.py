from copy import copy
from enum import Enum
from typing import no_type_check

from .case import CaseConstructor


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

    cls._Key = Enum('_Key', list(caseConstructors.keys()))

    def _init(self, key, value, orig_init=cls.__init__):
        self._key = key
        self._value = value
        orig_init(self)

    cls.__init__ = _init

    def _repr(self):
        return f'{type(self)}.{self._key.name}({self._value})'

    if '__repr__' not in cls.__dict__:
        cls.__repr__ = _repr

    def _str(self):
        return f'<{type(self)}.{self._key.name}: {self._value}>'

    if '__str__' not in cls.__dict__:
        cls.__str__ = _str

    def _eq(self, other, cls=cls):
        if not isinstance(other, cls):
            return False

        return self._key == other._key and self._value == other._value

    if '__eq__' not in cls.__dict__:
        cls.__eq__ = _eq

    for caseName, key in cls._Key.__members__.items():

        def constructor(cls,
                        *args,
                        _key=key,
                        _caseConstructor=caseConstructors[caseName]):
            return cls(key=_key, value=_caseConstructor.constructCase(*args))

        if hasattr(cls, caseName):
            raise AttributeError(
                f'{cls} should not have a default value for {caseName}, as this will be a generated constructor'
            )

        setattr(cls, caseName, classmethod(constructor))

        def accessor(self, _key=key):
            if self._key != _key:
                raise AttributeError(
                    f'{self} was constructed as case {self._key.name}, so {_key.name} is not accessible'
                )

            return self._value

        if caseName.lower() not in cls.__dict__:
            setattr(cls, caseName.lower(), accessor)

    def match(self, _caseConstructors=caseConstructors, **kwargs):
        upperKeys = {k: k.upper() for k in kwargs.keys()}

        assert set(upperKeys.values()) == set(
            _caseConstructors.keys()
        ), f'Pattern match on {self} ({upperKeys.values()}) is over- or under-specified vs. {_caseConstructors.keys()}'

        for key, callback in kwargs.items():
            if self._key == type(self)._Key[upperKeys[key]]:
                return _caseConstructors[upperKeys[key]].deconstructCase(
                    self._value, callback)

        raise ValueError(
            f'{self} failed pattern match against all of: {predicates}')

    if 'match' not in cls.__dict__:
        cls.match = match

    return cls
