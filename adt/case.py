from typing import TYPE_CHECKING, Any, Callable, Generic, Tuple, Type, TypeVar, Union

_T = TypeVar('_T')
_U = TypeVar('_U')


class TupleConstructor:
    def __init__(self, types: Tuple[Type[Any], ...]):
        self._types = types
        super().__init__()

    def constructCase(self, *args: Any) -> Tuple[Any, ...]:
        assert len(args) == len(self._types)
        return (*args, )

    def deconstructCase(self, value: Tuple[Any, ...],
                        callback: Callable[..., _T]) -> _T:
        assert len(value) == len(self._types)
        return callback(*value)

    def getTypes(self) -> Any:
        return self._types

    def __repr__(self) -> str:
        typeString = ', '.join((str(t) for t in self._types))
        return f'Case[{typeString}]'


class IdentityConstructor:
    def __init__(self, argType: Type[Any]):
        self._argType = argType
        super().__init__()

    def constructCase(self, arg: _T) -> _T:
        return arg

    def deconstructCase(self, value: _T, callback: Callable[[_T], _U]) -> _U:
        return callback(value)

    def getTypes(self) -> Any:
        return self._argType

    def __repr__(self) -> str:
        return f'Case[{self._argType}]'


class CaseConstructor:
    AnyConstructor = Union["CaseConstructor", IdentityConstructor,
                           TupleConstructor]

    def constructCase(self) -> None:
        return None

    def deconstructCase(self, value: None, callback: Callable[[], _T]) -> _T:
        return callback()

    def getTypes(self) -> None:
        return None

    def __getitem__(self, params: Union[None, Type[Any], Tuple[Type[Any], ...]]
                    ) -> AnyConstructor:
        if params is None:
            return self
        elif isinstance(params, tuple):
            return TupleConstructor(params)
        else:
            return IdentityConstructor(params)

    def __repr__(self) -> str:
        return 'Case'


if TYPE_CHECKING:
    # Simple shim to capture the type arguments for use in the mypy plugin
    class CaseT(Generic[_T]):
        pass

    class CaseMeta(type):
        def __getitem__(self, params: _T) -> CaseT[_T]:
            pass

    class Case(CaseT[None], metaclass=CaseMeta):
        pass
else:
    Case = CaseConstructor()

# Case
# Case[int]
# Case[int, str]

# class TestClass:
#     a: Case
#     b: Case[None]
#     c: Case[int]
#     d: Case[int, str]
