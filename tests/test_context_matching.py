import unittest

from adt import Case, adt


@adt
class ContextMatching:
    EMPTY: Case
    INTEGER: Case[int]
    STRINGS: Case[str, str]


class TestContextManagerAccessors(unittest.TestCase):
    def test_empty(self):
        foo = ContextMatching.EMPTY()

        with foo.empty:
            self.assertTrue(True)

        with foo.integer:
            self.assertTrue(False)

        with foo.strings:
            self.assertTrue(False)

    def test_integer(self):
        foo = ContextMatching.INTEGER(1)

        with foo.empty:
            self.assertTrue(False)

        with foo.integer as value:
            self.assertEqual(value, 1)

        with foo.strings:
            self.assertTrue(False)

    def test_strings(self):
        foo = ContextMatching.STRINGS("aaa", "bbb")

        with foo.empty:
            self.assertTrue(False)

        with foo.integer:
            self.assertTrue(False)

        with foo.strings as (string_1, string_2):
            self.assertEqual(string_1, "aaa")
            self.assertEqual(string_2, "bbb")
