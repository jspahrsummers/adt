import unittest
from typing import Generic, Tuple, TypeVar

from adt import Case, adt
from hypothesis import given
from hypothesis.strategies import (builds, deferred, from_type, integers, just,
                                   one_of, register_type_strategy, tuples)
from tests import helpers

_T = TypeVar('_T')


@adt
class ListADT(Generic[_T]):
    NIL: Case
    CONS: Case[_T, "ListADT[_T]"]


register_type_strategy(
    ListADT,
    one_of(
        builds(ListADT.NIL),
        builds(ListADT.CONS, integers(),
               deferred(lambda: from_type(ListADT)))))


class TestList(unittest.TestCase):
    def test_construction(self) -> None:
        xs = ListADT.CONS("a", ListADT.CONS("b", ListADT.NIL()))

        (x, xs) = xs.cons()
        self.assertEqual(x, "a")

        (x, xs) = xs.cons()
        self.assertEqual(x, "b")
        self.assertEqual(xs, ListADT.NIL())

    @given(from_type(ListADT))
    def test_equalsItself(self, xs: ListADT[_T]) -> None:
        self.assertEqual(xs, xs)

    @given(from_type(ListADT))
    def test_exhaustivePatternMatchSucceeds(self, xs: ListADT[_T]) -> None:
        self.assertTrue(xs.match(nil=lambda: True, cons=lambda x, xs: True))

    @given(from_type(ListADT))
    def test_inexhaustivePatternMatchThrows(self, xs: ListADT[_T]) -> None:
        with self.assertRaises(ValueError):
            xs.match()  # type: ignore

        with self.assertRaises(ValueError):
            xs.match(nil=lambda x: True)  # type: ignore

        with self.assertRaises(ValueError):
            xs.match(cons=lambda x: True)  # type: ignore

    @given(from_type(ListADT))
    def test_accessorsConsistentWithMatching(self, xs: ListADT[_T]) -> None:
        if xs.match(nil=lambda: False, cons=lambda x, xs: True):
            with self.assertRaises(AttributeError):
                xs.nil()

            self.assertIsNotNone(xs.cons())
            self.assertEqual(
                xs.cons(),
                xs.match(nil=helpers.invalidPatternMatch,
                         cons=lambda x, xs: (x, xs)))
        else:
            with self.assertRaises(AttributeError):
                xs.cons()

            self.assertEqual(
                xs.match(nil=lambda: "foo", cons=helpers.invalidPatternMatch),
                "foo")
