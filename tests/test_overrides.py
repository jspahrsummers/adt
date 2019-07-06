import unittest

from adt import Case, adt
from tests import helpers
from typing import Callable, Optional, TypeVar

_T = TypeVar('_T')


def optionality(x: _T) -> Optional[_T]:
    return x


@adt
class OverriddenAccessors:
    INTVALUE: Case[int]
    STRVALUE: Case[str]

    @property
    def intvalue(self) -> Optional[int]:
        return self.match(intvalue=lambda x: optionality(x),
                          strvalue=lambda _: None)

    @property
    def strvalue(self) -> Optional[str]:
        return self.match(intvalue=lambda _: None,
                          strvalue=lambda x: optionality(x))


@adt
class OverriddenMatch:
    INTVALUE: Case[int]
    STRVALUE: Case[str]

    def match(self, intvalue: Callable[[int], str],
              strvalue: Callable[[str], str]) -> str:
        try:
            x = self.intvalue()
        except:
            return strvalue(self.strvalue())

        return intvalue(x)


class TestOverrides(unittest.TestCase):
    def test_overriddenAccessorIntvalue(self) -> None:
        x = OverriddenAccessors.INTVALUE(5)
        self.assertEqual(x.intvalue, 5)
        self.assertIsNone(x.strvalue)
        self.assertEqual(
            x.match(intvalue=lambda x: x,
                    strvalue=helpers.invalidPatternMatch), 5)

    def test_overriddenAccessorStrvalue(self) -> None:
        x = OverriddenAccessors.STRVALUE("foobar")
        self.assertIsNone(x.intvalue)
        self.assertEqual(x.strvalue, "foobar")
        self.assertEqual(
            x.match(intvalue=helpers.invalidPatternMatch,
                    strvalue=lambda x: x), "foobar")

    def test_overriddenMatchIntvalue(self) -> None:
        x = OverriddenMatch.INTVALUE(5)
        self.assertEqual(x.intvalue(), 5)
        self.assertEqual(
            x.match(intvalue=lambda x: str(x),
                    strvalue=helpers.invalidPatternMatch), "5")

    def test_overriddenMatchStrvalue(self) -> None:
        x = OverriddenMatch.STRVALUE("foobar")
        self.assertEqual(x.strvalue(), "foobar")
        self.assertEqual(
            x.match(intvalue=helpers.invalidPatternMatch,
                    strvalue=lambda x: x), "foobar")