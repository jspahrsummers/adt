import unittest

from adt import Case, adt


@adt
class ContextMatching:
    EMPTY: Case
    INTEGER: Case[int]
    STRINGS: Case[str, str]

foo = ContextMatching.INTEGER(1)

with foo.empty:
    print("Is empty")

with foo.integer as value:
    print("Is integer:", value)

with foo.strings as (string_1, string_2):
    print("Is strings:", string_1, string_2)


@adt
class ContextMatching:
    NONE: Case
    OK: Case[int, float]


with foo.ok[:4, :] as (val_1, val_2):
    print("val_1 less than 4 and val_2 anything")

with foo.ok[4:, 1.3:9.9] as (val_1, val_2):
    print("val_1 4 or higher and val_2 between 1.3 and 9.9")

with foo.ok as (val_1, val_2):
    print("Unhandled ok cases")


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
