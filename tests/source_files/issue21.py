from adt import adt, Case


@adt
class Cmd:
    CASE0: Case
    CASE1: Case[str]
    CASE2: Case[str, str]
    CASE3: Case[str, str, str]
