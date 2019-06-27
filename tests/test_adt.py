import unittest
from typing import Any, Generic, NoReturn, Tuple, TypeVar

from hypothesis import given
from hypothesis.strategies import (builds, deferred, from_type, integers, just,
                                   one_of, register_type_strategy, text,
                                   tuples)

from adt.decorator import adt

_L = TypeVar('_L')
_R = TypeVar('_R')


@adt
class EitherADT(Generic[_L, _R]):
    LEFT: _L
    RIGHT: _R


any_types = one_of(integers(), text())

register_type_strategy(
    EitherADT,
    one_of(builds(EitherADT.LEFT, any_types), builds(EitherADT.RIGHT,
                                                     any_types)))

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


def invalidPatternMatch(x: Any) -> NoReturn:
    assert False, 'Pattern matching failed'


class TestADT(unittest.TestCase):
    def test_either(self) -> None:
        e: EitherADT[int, str] = EitherADT.LEFT(5)
        self.assertEqual(e, EitherADT.LEFT(5))
        self.assertNotEqual(e, EitherADT.RIGHT("foobar"))
        self.assertEqual(e.left(), 5)
        self.assertIsNone(e.right())
        self.assertEqual(
            e.match(left=lambda n: str(n + 1), right=lambda s: s + "z"), "6")

        e = EitherADT.RIGHT("foobar")
        self.assertNotEqual(e, EitherADT.LEFT(5))
        self.assertEqual(e, EitherADT.RIGHT("foobar"))
        self.assertIsNone(e.left())
        self.assertEqual(e.right(), "foobar")
        self.assertEqual(
            e.match(left=lambda n: str(n + 1), right=lambda s: s + "z"),
            "foobarz")

    @given(from_type(EitherADT))
    def test_eitherEqualsItself(self, e: EitherADT[_L, _R]) -> None:
        self.assertEqual(e, e)

    @given(from_type(EitherADT))
    def test_eitherExhaustivePatternMatchSucceeds(self, e: EitherADT[_L, _R]
                                                  ) -> None:
        self.assertTrue(e.match(left=lambda x: True, right=lambda x: True))

    @given(from_type(EitherADT))
    def test_eitherInexhaustivePatternMatchThrows(self, e: EitherADT[_L, _R]
                                                  ) -> None:
        with self.assertRaises((AssertionError, RuntimeError)):
            e.match()  # type: ignore
        with self.assertRaises((AssertionError, RuntimeError)):
            e.match(left=lambda x: True)  # type: ignore
        with self.assertRaises((AssertionError, RuntimeError)):
            e.match(right=lambda x: True)  # type: ignore

    @given(from_type(EitherADT))
    def test_eitherAccessorsAndMatchConsistent(self,
                                               e: EitherADT[_L, _R]) -> None:
        if e.match(left=lambda x: False, right=lambda x: True):
            self.assertIsNone(e.left())
            self.assertIsNotNone(e.right())
            self.assertEqual(
                e.right(), e.match(left=invalidPatternMatch,
                                   right=lambda x: x))
        else:
            self.assertIsNotNone(e.left())
            self.assertIsNone(e.right())
            self.assertEqual(
                e.left(), e.match(left=lambda x: x, right=invalidPatternMatch))

    def test_list(self) -> None:
        xs = ListADT.CONS(("a", ListADT.CONS(("b", ListADT.NIL(None)))))

        (x, xs) = xs.cons()
        self.assertEqual(x, "a")

        (x, xs) = xs.cons()
        self.assertEqual(x, "b")
        self.assertEqual(xs, ListADT.NIL(None))

    @given(from_type(ListADT))
    def test_listEqualsItself(self, xs: ListADT[_T]) -> None:
        self.assertEqual(xs, xs)

    @given(from_type(ListADT))
    def test_listExhaustivePatternMatchSucceeds(self, xs: ListADT[_T]) -> None:
        self.assertTrue(xs.match(nil=lambda x: True, cons=lambda x: True))

    @given(from_type(ListADT))
    def test_listInexhaustivePatternMatchThrows(self, xs: ListADT[_T]) -> None:
        with self.assertRaises((AssertionError, RuntimeError)):
            xs.match()  # type: ignore
        with self.assertRaises((AssertionError, RuntimeError)):
            xs.match(nil=lambda x: True)  # type: ignore
        with self.assertRaises((AssertionError, RuntimeError)):
            xs.match(cons=lambda x: True)  # type: ignore

    @given(from_type(ListADT))
    def test_listAccessorsAndMatchConsistent(self, xs: ListADT[_T]) -> None:
        if xs.match(nil=lambda x: False, cons=lambda x: True):
            self.assertIsNotNone(xs.cons())
            self.assertEqual(
                xs.cons(), xs.match(nil=invalidPatternMatch, cons=lambda x: x))
        else:
            self.assertIsNone(xs.cons())

            with self.assertRaises(AssertionError):
                xs.match(nil=lambda x: x, cons=invalidPatternMatch)
