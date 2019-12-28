from typing import Optional
from adt import adt, Case


@adt
class ExampleADT:
    EMPTY: Case
    INTEGER: Case[int]
    STRING_PAIR: Case[str, str]

    @property
    def safe_integer(self) -> Optional[int]:
        return self.match(empty=lambda: None,
                          integer=lambda n: n,
                          string_pair=lambda a, b: None)
