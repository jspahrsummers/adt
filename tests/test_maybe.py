import unittest
from typing import Callable, Generic, TypeVar

from adt import Case, adt
from hypothesis import given
from hypothesis.strategies import (builds, from_type, just, one_of,
                                   register_type_strategy)
from tests import helpers

_T = TypeVar('_T')
_U = TypeVar('_U')


@adt
class Maybe(Generic[_T]):
    NOTHING: Case
    JUST: Case[_T]

    def map(self, fn: Callable[[_T], _U]) -> "Maybe[_U]":
        return self.match(just=lambda x: Maybe.JUST(fn(x)),
                          nothing=lambda: Maybe.NOTHING())

    def flatMap(self, fn: Callable[[_T], "Maybe[_U]"]) -> "Maybe[_U]":
        return self.match(just=lambda x: fn(x),
                          nothing=lambda: Maybe.NOTHING())


nothings = builds(Maybe.NOTHING)
justs = builds(Maybe.JUST, helpers.any_types)

register_type_strategy(Maybe, one_of(nothings, justs))


class TestMaybe(unittest.TestCase):
    @given(from_type(Maybe))
    def test_equalsItself(self, m: Maybe[_T]) -> None:
        self.assertEqual(m, m)

    @given(from_type(Maybe))
    def test_mapIdentity(self, m: Maybe[_T]) -> None:
        self.assertEqual(m.map(lambda x: x), m)

    @given(nothings)
    def test_mapNothingReturnsNothing(self, m: Maybe[_T]) -> None:
        mapped = m.map(lambda _: "foobar")
        self.assertEqual(mapped, Maybe.NOTHING())

    @given(justs)
    def test_mapJust(self, m: Maybe[_T]) -> None:
        mapped = m.map(lambda _: "foobar")
        self.assertEqual(mapped, Maybe.JUST("foobar"))

    @given(from_type(Maybe))
    def test_flatMapIdentity(self, m: Maybe[_T]) -> None:
        self.assertEqual(m.flatMap(lambda x: Maybe.JUST(x)), m)

    @given(from_type(Maybe))
    def test_flatMapToNothingReturnsNothing(self, m: Maybe[_T]) -> None:
        self.assertEqual(m.flatMap(lambda _: Maybe.NOTHING()), Maybe.NOTHING())

    @given(nothings)
    def test_flatMapOfNothingReturnsNothing(self, m: Maybe[_T]) -> None:
        self.assertEqual(m.flatMap(lambda _: Maybe.JUST("foobar")),
                         Maybe.NOTHING())

    @given(justs)
    def test_flatMapOfJust(self, m: Maybe[_T]) -> None:
        self.assertEqual(m.flatMap(lambda _: Maybe.JUST("foobar")),
                         Maybe.JUST("foobar"))
