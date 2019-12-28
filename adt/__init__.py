from typing import TYPE_CHECKING

from .case import Case
from .decorator import adt

if TYPE_CHECKING:
    from .case import CaseConstructor
