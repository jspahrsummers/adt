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
        self.assertNotEqual(e, EitherADT.Right("foobar"))
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
