from hypothesis.strategies import integers, one_of, text
from typing import Any, NoReturn

any_types = one_of(integers(), text())


def invalidPatternMatch(x: Any) -> NoReturn:
    assert False, 'Pattern matching failed'
