from decimal import Decimal
from mypy.nodes import AssignmentStmt, ClassDef, NameExpr, Var
from mypy.plugin import Plugin, ClassDefContext

from typing import Callable, Optional, Type


class ADTPlugin(Plugin):
    _ADT_DECORATOR = 'adt.decorator.adt'

    def _transform_class(self, context: ClassDefContext) -> None:
        print(f'_transform_class: {context}')

        cls = context.cls
        typeInfo = cls.info

        for statement in cls.defs.body:
            if not isinstance(statement, AssignmentStmt):
                continue

            for lval in statement.lvalues:
                if not isinstance(lval, NameExpr):
                    continue

                node = typeInfo.names[lval.name].node
                if not isinstance(node, Var):
                    continue

                print(f'Identified node {node}')

    def get_class_decorator_hook(
            self,
            fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        if fullname != self._ADT_DECORATOR:
            return None

        return self._transform_class


def plugin(version: str) -> Type[Plugin]:
    assert Decimal(version) >= Decimal('0.711')
    return ADTPlugin