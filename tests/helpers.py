import os
from typing import Any, NoReturn

import hypothesis
from hypothesis.strategies import integers, one_of, text

hypothesis.settings.register_profile("ci", max_examples=1000, deadline=100)
hypothesis.settings.register_profile("dev", max_examples=100, deadline=50)
hypothesis.settings.load_profile(
    os.getenv(u'HYPOTHESIS_PROFILE', default='dev'))

any_types = one_of(integers(), text())


def invalidPatternMatch(*args: Any) -> NoReturn:
    assert False, 'Pattern matching failed'
