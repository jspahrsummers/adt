from decimal import Decimal
from mypy.nodes import ARG_POS, Argument, AssignmentStmt, ClassDef, NameExpr, Var
from mypy.plugin import Plugin, ClassDefContext
from mypy.plugins.common import add_method

from typing import Any, Callable, Dict, Optional, Type

import mypy.types


class ADTPlugin(Plugin):
    _ADT_DECORATOR = 'adt.decorator.adt'

    def _transform_class(self, context: ClassDefContext) -> None:
        print(f'_transform_class: {context}')

        cls = context.cls
        typeInfo = cls.info

        cases = [
            typeInfo[lval.name].node for statement in cls.defs.body
            if isinstance(statement, AssignmentStmt)
            for lval in statement.lvalues if isinstance(lval, NameExpr)
        ]

        for case in cases:
            if not isinstance(case, Var):
                continue

            print(f'Identified ADT case {case}')

            # Argument(variable=case, type_annotation=typeInfo[case.name()].type, initializer=None, kind=ARG_POS)

            assert case.type

            # Accessor method (lowercase)
            add_method(context,
                       name=case.name().lower(),
                       args=[],
                       return_type=case.type)

    def get_class_decorator_hook(
            self,
            fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        if fullname != self._ADT_DECORATOR:
            return None

        return self._transform_class


def plugin(version: str) -> Type[Plugin]:
    assert Decimal(version) >= Decimal('0.711')
    return ADTPlugin