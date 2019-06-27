from decimal import Decimal
from mypy.plugin import Plugin

from typing import Type


class ADTPlugin(Plugin):
    pass


def plugin(version: str) -> Type[Plugin]:
    assert Decimal(version) >= Decimal('0.711')
    return ADTPlugin