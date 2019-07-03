from typing import Any, Callable, Tuple, Type, TypeVar, Union

_T = TypeVar('_T')


class TupleConstructor:
    def __init__(self, tupleSize: int):
        self._tupleSize = tupleSize
        super().__init__()

    def constructCase(self, *args: Any) -> Tuple[Any, ...]:
        assert len(args) == self._tupleSize
        return (*args, )


class IdentityConstructor:
    def constructCase(self, arg: _T) -> _T:
        return arg


class CaseDefinition:
    def constructCase(self) -> None:
        return None

    def __getitem__(self, params: Union[Type[Any], Tuple[Type[Any], ...]]
                    ) -> Union[IdentityConstructor, TupleConstructor]:
        if isinstance(params, tuple):
            return TupleConstructor(len(params))
        else:
            return IdentityConstructor()


Case = CaseDefinition()
Case
Case[int]
Case[int, str]
