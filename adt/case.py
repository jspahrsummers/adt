from typing import Any, Callable, Tuple, Type, TypeVar, Union

_T = TypeVar('_T')


class TupleConstructor:
    def __init__(self, types: Tuple[Type[Any], ...]):
        self._types = types
        super().__init__()

    def constructCase(self, *args: Any) -> Tuple[Any, ...]:
        assert len(args) == len(self._types)
        return (*args, )

    def __repr__(self) -> str:
        typeString = ', '.join((str(t) for t in self._types))
        return f'Case[{typeString}]'


class IdentityConstructor:
    def __init__(self, argType: Type[Any]):
        self._argType = argType
        super().__init__()

    def constructCase(self, arg: _T) -> _T:
        return arg

    def __repr__(self) -> str:
        return f'Case[{self._argType}]'


class CaseConstructor:
    AnyConstructor = Union["CaseConstructor", IdentityConstructor,
                           TupleConstructor]

    def constructCase(self) -> None:
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


Case = CaseConstructor()
# Case
# Case[int]
# Case[int, str]

# class TestClass:
#     a: Case
#     b: Case[None]
#     c: Case[int]
#     d: Case[int, str]