import unittest

from adt import Case, adt


@adt
class Expression:
    LITERAL: Case[float]


class TestHash(unittest.TestCase):
    def test_hash_correct(self) -> None:
        a = Expression.LITERAL(0.0)
        b = Expression.LITERAL(0.0)
        self.assertEqual(hash(a), hash(b))
