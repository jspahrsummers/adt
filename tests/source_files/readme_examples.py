from adt import adt, Case
from typing import Dict, TypeVar, Generic, Tuple, Optional

# TODO: This could probably be extracted from README.md at test-time


# ADTs are useful for a variety of data structures, including binary trees:
@adt
class Tree:
    EMPTY: Case
    LEAF: Case[int]
    NODE: Case["Tree", "Tree"]


# Abstract syntax trees (like you might implement as part of a parser, compiler, or interpreter):
@adt
class Expression:
    LITERAL: Case[float]
    UNARY_MINUS: Case["Expression"]
    ADD: Case["Expression", "Expression"]
    MINUS: Case["Expression", "Expression"]
    MULTIPLY: Case["Expression", "Expression"]
    DIVIDE: Case["Expression", "Expression"]


# Or more generic versions of a variant type, like an Either type that represents a type A or a type B, but not both:
L = TypeVar('L')
R = TypeVar('R')


@adt
class Either(Generic[L, R]):
    LEFT: Case[L]
    RIGHT: Case[R]


# Defined in some other module, perhaps
def some_operation() -> Either[Exception, int]:
    return Either.RIGHT(0)


# Run some_operation, and handle the success or failure
default_value = 5
some_operation().match(
    # In this case, we're going to ignore any exception we receive
    left=lambda ex: default_value,
    right=lambda result: result)

# One can do the same thing with the Expression type above (just more cases to match):
e: Expression = Expression.LITERAL(0.1)
result: int = e.match(
    literal=lambda n: 1,
    unary_minus=lambda expr: 2,
    add=lambda lhs, rhs: 3,
    minus=lambda lhs, rhs: 4,
    multiply=lambda lhs, rhs: 5,
    divide=lambda lhs, rhs: 6,
)


# Defining an ADT
@adt
class MyADT:
    FIRST_CASE: Case
    SECOND_CASE: Case
    STRING_CASE: Case[str]
    LOTS_OF_DATA_CASE: Case[int, str, str, Dict[int, int]]


T = TypeVar('T')


@adt
class LinkedList(Generic[T]):
    NIL: Case
    CONS: Case[T, "LinkedList[T]"]


@adt
class ExampleADT:
    EMPTY: Case
    INTEGER: Case[int]
    STRING_PAIR: Case[str, str]

    @property
    def safe_integer(self) -> Optional[int]:
        return self.match(empty=lambda: None,
                          integer=lambda n: n,
                          string_pair=lambda _a, _b: None)

    @property
    def safe_string_pair(self) -> Optional[Tuple[str, str]]:
        return self.match(empty=lambda: None,
                          integer=lambda: None,
                          string_pair=lambda a, b: tuple(a, b))


is_empty: None = ExampleADT.EMPTY().empty()
is_integer: int = ExampleADT.INTEGER(1).integer()
is_string_pair: Tuple[str, str] = ExampleADT.STRING_PAIR("foo",
                                                         "bar").string_pair()


def test_safe_properties(example_adt: ExampleADT):
    is_safe_integer: Optional[int] = example_adt.safe_integer()
    is_safe_string_pair: Optional[
        Tuple[str, str]] = example_adt.safe_string_pair()
