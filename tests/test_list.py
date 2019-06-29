import unittest
from typing import Generic, Tuple, TypeVar

from adt.decorator import adt
from hypothesis import given
from hypothesis.strategies import (builds, deferred, from_type, just, one_of,
                                   register_type_strategy, tuples, integers)

import helpers

_T = TypeVar('_T')


@adt
class ListADT(Generic[_T]):
    NIL: None
    CONS: Tuple[_T, "ListADT[_T]"]


register_type_strategy(
    ListADT,
    one_of(
        builds(ListADT.NIL, just(None)),
        builds(ListADT.CONS,
               tuples(integers(), deferred(lambda: from_type(ListADT))))))


class TestList(unittest.TestCase):
    def test_construction(self) -> None:
        xs = ListADT.CONS(("a", ListADT.CONS(("b", ListADT.NIL(None)))))

        (x, xs) = xs.cons()
        self.assertEqual(x, "a")

        (x, xs) = xs.cons()
        self.assertEqual(x, "b")
        self.assertEqual(xs, ListADT.NIL(None))

    @given(from_type(ListADT))
    def test_equalsItself(self, xs: ListADT[_T]) -> None:
        self.assertEqual(xs, xs)

    @given(from_type(ListADT))
    def test_exhaustivePatternMatchSucceeds(self, xs: ListADT[_T]) -> None:
        self.assertTrue(xs.match(nil=lambda x: True, cons=lambda x: True))

    @given(from_type(ListADT))
    def test_inexhaustivePatternMatchThrows(self, xs: ListADT[_T]) -> None:
        with self.assertRaises((AssertionError, RuntimeError)):
            xs.match()  # type: ignore

        with self.assertRaises((AssertionError, RuntimeError)):
            xs.match(nil=lambda x: True)  # type: ignore

        with self.assertRaises((AssertionError, RuntimeError)):
            xs.match(cons=lambda x: True)  # type: ignore

    @given(from_type(ListADT))
    def test_accessorsConsistentWithMatching(self, xs: ListADT[_T]) -> None:
        if xs.match(nil=lambda x: False, cons=lambda x: True):
            self.assertIsNotNone(xs.cons())
            self.assertEqual(
                xs.cons(),
                xs.match(nil=helpers.invalidPatternMatch, cons=lambda x: x))
        else:
            self.assertIsNone(xs.cons())
            self.assertEqual(
                xs.match(nil=lambda x: "foo",
                         cons=helpers.invalidPatternMatch), "foo")
