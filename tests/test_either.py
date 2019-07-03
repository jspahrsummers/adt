import unittest
from typing import Generic, TypeVar

from adt import Case, adt
from hypothesis import given
from hypothesis.strategies import (builds, from_type, one_of,
                                   register_type_strategy)
from tests import helpers

_L = TypeVar('_L')
_R = TypeVar('_R')


@adt
class Either(Generic[_L, _R]):
    LEFT: Case[_L]
    RIGHT: Case[_R]


register_type_strategy(
    Either,
    one_of(builds(Either.LEFT, helpers.any_types),
           builds(Either.RIGHT, helpers.any_types)))


class TestEither(unittest.TestCase):
    def test_left(self) -> None:
        e: Either[int, str] = Either.LEFT(5)
        self.assertEqual(e, Either.LEFT(5))
        self.assertEqual(e.left(), 5)

        self.assertNotEqual(e, Either.RIGHT(5))
        with self.assertRaises(AttributeError):
            e.right()

        self.assertEqual(
            e.match(left=lambda n: n + 1, right=helpers.invalidPatternMatch),
            6)

    def test_right(self) -> None:
        e: Either[int, str] = Either.RIGHT("foobar")
        self.assertEqual(e, Either.RIGHT("foobar"))
        self.assertEqual(e.right(), "foobar")

        self.assertNotEqual(e, Either.LEFT("foobar"))
        with self.assertRaises(AttributeError):
            e.left()

        self.assertEqual(
            e.match(left=helpers.invalidPatternMatch, right=lambda s: s + "z"),
            "foobarz")

    @given(from_type(Either))
    def test_equalsItself(self, e: Either[_L, _R]) -> None:
        self.assertEqual(e, e)

    @given(from_type(Either))
    def test_exhaustivePatternMatchSucceeds(self, e: Either[_L, _R]) -> None:
        self.assertTrue(e.match(left=lambda x: True, right=lambda x: True))

    @given(from_type(Either))
    def test_inexhaustivePatternMatchThrows(self, e: Either[_L, _R]) -> None:
        with self.assertRaises(ValueError):
            e.match()  # type: ignore

        with self.assertRaises(ValueError):
            e.match(left=lambda x: True)  # type: ignore

        with self.assertRaises(ValueError):
            e.match(right=lambda x: True)  # type: ignore

    @given(from_type(Either))
    def test_accessorsConsistentWithMatching(self, e: Either[_L, _R]) -> None:
        if e.match(left=lambda x: False, right=lambda x: True):
            self.assertIsNotNone(e.right())

            with self.assertRaises(AttributeError):
                e.left()

            self.assertEqual(
                e.right(),
                e.match(left=helpers.invalidPatternMatch, right=lambda x: x))
        else:
            self.assertIsNotNone(e.left())

            with self.assertRaises(AttributeError):
                e.right()

            self.assertEqual(
                e.left(),
                e.match(left=lambda x: x, right=helpers.invalidPatternMatch))
