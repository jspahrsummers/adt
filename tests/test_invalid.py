import unittest
from typing import Generic, Optional, TypeVar

from adt import Case, adt

_T = TypeVar('_T')

invalid_defined: bool

try:

    @adt
    class Invalid(Generic[_T]):
        CASE: Case[Optional[_T]] = None

    invalid_defined = True
except AttributeError as e:
    print(f'Expected failure: {e}')
    invalid_defined = False


class TestInvalid(unittest.TestCase):
    def test_cannotSetDefaultValuesForCases(self) -> None:
        self.assertFalse(invalid_defined)