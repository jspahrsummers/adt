import unittest
from typing import Generic, TypeVar

from adt.decorator import adt
from hypothesis import given
from hypothesis.strategies import (builds, from_type, one_of,
                                   register_type_strategy)
from tests import helpers

_A = TypeVar('_A')
_B = TypeVar('_B')


@adt
class UnaryOption(Generic[_A]):
    ONE: _A


@adt
class BinaryOption(UnaryOption[_A], Generic[_A, _B]):
    TWO: _B


register_type_strategy(UnaryOption, builds(UnaryOption.ONE, helpers.any_types))

binaryOne = builds(BinaryOption.ONE, helpers.any_types)
binaryTwo = builds(BinaryOption.TWO, helpers.any_types)

register_type_strategy(BinaryOption, one_of(binaryOne, binaryTwo))


class TestSubclassing(unittest.TestCase):
    @given(from_type(UnaryOption))
    def test_unary(self, opt: UnaryOption[_A]) -> None:
        self.assertEqual(opt, opt)
        self.assertEqual(UnaryOption.ONE(opt.one()), opt)

        self.assertEqual(opt.match(one=lambda x: "foobar"), "foobar")

    @given(from_type(BinaryOption))
    def test_binaryEqualsItself(self, opt: BinaryOption[_A, _B]) -> None:
        self.assertEqual(opt, opt)

    @given(binaryOne)
    def test_binaryOne(self, opt: BinaryOption[_A, _B]) -> None:
        self.assertIsNotNone(opt.one())
        self.assertIsNone(opt.two())
        self.assertEqual(BinaryOption.ONE(opt.one()), opt)
        self.assertNotEqual(BinaryOption.TWO(opt.one()), opt)
        self.assertNotEqual(UnaryOption.ONE(opt.one()), opt)

        self.assertEqual(
            opt.match(one=lambda x: "foobar", two=helpers.invalidPatternMatch),
            "foobar")

    @given(binaryTwo)
    def test_binaryTwo(self, opt: BinaryOption[_A, _B]) -> None:
        self.assertIsNone(opt.one())
        self.assertIsNotNone(opt.two())
        self.assertEqual(BinaryOption.TWO(opt.two()), opt)
        self.assertNotEqual(BinaryOption.ONE(opt.two()), opt)
        self.assertNotEqual(UnaryOption.ONE(opt.two()), opt)

        self.assertEqual(
            opt.match(one=helpers.invalidPatternMatch, two=lambda x: "foobar"),
            "foobar")
