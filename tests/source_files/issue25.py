from adt import adt, Case


@adt
class Expression:
    LITERAL: Case[float]


result: None = Expression.LITERAL(0.1).match(literal=lambda n: None)
