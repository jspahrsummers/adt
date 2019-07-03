from abc import ABC, abstractmethod
from typing import Any, Generic, Tuple, Type, TypeVar, Union, cast

_T = TypeVar('_T')
_Arg = TypeVar('_Arg')


class CaseInstantiation(ABC, Generic[_T, _Arg]):
    @abstractmethod
    def construct(self, *args: _Arg) -> _T:
        pass


class NoneCase(CaseInstantiation[None, None]):
    def construct(self, *args: None) -> None:
        assert len(args) == 0
        return None


class UnaryCase(CaseInstantiation[_T, _T], Generic[Type[_T]]):
    def __init__(self, argType: Type[_T]):
        self._argType = argType
        super().__init__()

    def construct(self, *args: _T) -> _T:
        assert len(args) == 1
        return args[0]


class TupleCase(CaseInstantiation[Tuple[_Arg, ...], _Arg], Generic[_Arg]):
    def __init__(self, tupleSize: int, argTypes: Tuple[Type[_Arg], ...]):
        self._argTypes = argTypes
        self._tupleSize = tupleSize
        super().__init__()

    def construct(self, *args: _Arg) -> Tuple[_Arg, ...]:
        assert len(args) == self._tupleSize
        return (*args, )


class CaseDefinition(NoneCase):
    def __getitem__(self, params: Union[Type[_T], Tuple[Type[_T], ...]]
                    ) -> CaseInstantiation[Any, _T]:
        if isinstance(params, tuple):
            return TupleCase(len(params), params)
        else:
            return UnaryCase(argType=params)


Case = CaseDefinition()
Case
Case[int]
Case[int, str]
