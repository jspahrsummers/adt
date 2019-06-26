from adt.decorator import adt
from typing import Generic, Tuple, TypeVar

import unittest

_L = TypeVar('_L')
_R = TypeVar('_R')


@adt
class EitherADT(Generic[_L, _R]):
    LEFT: _L
    RIGHT: _R


_T = TypeVar('_T')


@adt
class ListADT(Generic[_T]):
    NIL: None
    CONS: Tuple[_T, "ListADT[_T]"]


class TestADT(unittest.TestCase):
    def test_either(self) -> None:
        e = EitherADT.LEFT(5)
        self.assertEqual(e, EitherADT.LEFT(5))
        self.assertNotEqual(e, EitherADT.RIGHT("foobar"))
        self.assertEqual(e.left, 5)
        self.assertIsNone(e.right)
        self.assertEqual(
            e.match(left=lambda n: n + 1, right=lambda s: s + "z"), 6)

        e = EitherADT.RIGHT("foobar")
        self.assertNotEqual(e, EitherADT.LEFT(5))
        self.assertEqual(e, EitherADT.RIGHT("foobar"))
        self.assertIsNone(e.left)
        self.assertEqual(e.right, "foobar")
        self.assertEqual(
            e.match(left=lambda n: n + 1, right=lambda s: s + "z"), "foobarz")

    def test_list(self) -> None:
        xs = ListADT.CONS(("a", ListADT.CONS(("b", ListADT.NIL(None)))))

        (x, xs) = xs.cons
        self.assertEqual(x, "a")

        (x, xs) = xs.cons
        self.assertEqual(x, "b")
        self.assertEqual(xs, ListADT.NIL(None))