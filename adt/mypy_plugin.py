from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Type

import mypy.types
from mypy.nodes import (ARG_POS, MDEF, Argument, AssignmentStmt, Block,
                        ClassDef, Decorator, FuncDef, NameExpr, PassStmt,
                        SymbolTableNode, TypeVarExpr, Var)
from mypy.plugin import ClassDefContext, Plugin
from mypy.plugins.common import add_method
from mypy.semanal import set_callable_name
from mypy.typevars import fill_typevars
from mypy.util import get_unique_redefinition_name


class ADTPlugin(Plugin):
    _ADT_DECORATOR = 'adt.decorator.adt'

    # This is mypy.plugins.common.add_method() extended to support class methods.
    #
    # See original code at https://github.com/python/mypy/blob/17b68c6b7eaa76853422544e32b1d6c5c3acc55a/mypy/plugins/common.py#L81,
    # and license at https://github.com/python/mypy/blob/17b68c6b7eaa76853422544e32b1d6c5c3acc55a/LICENSE.
    def _add_method(
            self,
            ctx: ClassDefContext,
            name: str,
            args: List[Argument],
            return_type: mypy.types.Type,
            self_type: Optional[mypy.types.Type] = None,
            tvar_def: Optional[mypy.types.TypeVarDef] = None,
            is_classmethod: bool = False,
    ) -> None:
        """Adds a new method to a class.
        """
        info = ctx.cls.info

        # First remove any previously generated methods with the same name
        # to avoid clashes and problems in new semantic analyzer.
        if name in info.names:
            sym = info.names[name]
            if sym.plugin_generated and isinstance(sym.node, FuncDef):
                ctx.cls.defs.body.remove(sym.node)

        if is_classmethod:
            first = Argument(
                Var('cls'),
                # Working around python/mypy#5416.
                # This should be: mypy.types.TypeType.make_normalized(self_type)
                mypy.types.AnyType(mypy.types.TypeOfAny.implementation_artifact
                                   ),
                None,
                ARG_POS)
        else:
            self_type = self_type or fill_typevars(info)
            first = Argument(Var('self'), self_type, None, ARG_POS)

        args = [first] + args

        function_type = ctx.api.named_type('__builtins__.function')

        arg_types, arg_names, arg_kinds = [], [], []
        for arg in args:
            assert arg.type_annotation, 'All arguments must be fully typed.'
            arg_types.append(arg.type_annotation)
            arg_names.append(arg.variable.name())
            arg_kinds.append(arg.kind)

        print(f'Arg types: {arg_types}')
        print(f'Arg names: {arg_names}')

        signature = mypy.types.CallableType(arg_types, arg_kinds, arg_names,
                                            return_type, function_type)
        if tvar_def:
            signature.variables = [tvar_def]

        func = FuncDef(name, args, Block([PassStmt()]))
        func.info = info
        func.type = set_callable_name(signature, func)
        func._fullname = info.fullname() + '.' + name
        func.line = info.line

        # NOTE: we would like the plugin generated node to dominate, but we still
        # need to keep any existing definitions so they get semantically analyzed.
        if name in info.names:
            # Get a nice unique name instead.
            r_name = get_unique_redefinition_name(name, info.names)
            info.names[r_name] = info.names[name]

        info.defn.defs.body.append(func)

        if is_classmethod:
            v = Var(name, func.type)
            v.is_classmethod = True
            v.info = info
            v._fullname = func._fullname
            dec = Decorator(func, [NameExpr('classmethod')], v)
            info.defn.defs.body.append(dec)

            info.names[name] = SymbolTableNode(MDEF,
                                               dec,
                                               plugin_generated=True)
        else:
            info.names[name] = SymbolTableNode(MDEF,
                                               func,
                                               plugin_generated=True)

    def _transform_class(self, context: ClassDefContext) -> None:
        cls = context.cls
        typeInfo = cls.info

        instanceType = fill_typevars(typeInfo)
        assert isinstance(instanceType, mypy.types.Instance)

        cases = [
            typeInfo[lval.name].node for statement in cls.defs.body
            if isinstance(statement, AssignmentStmt)
            for lval in statement.lvalues if isinstance(lval, NameExpr)
        ]

        for case in cases:
            if not isinstance(case, Var):
                continue

            print(f'Identified ADT case {case}')

            assert case.type

            # Constructor method
            self._add_method(context,
                             name=case.name(),
                             args=[
                                 Argument(variable=case,
                                          type_annotation=case.type,
                                          initializer=None,
                                          kind=ARG_POS)
                             ],
                             return_type=instanceType,
                             is_classmethod=True)

            # Accessor method (lowercase)
            self._add_method(context,
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
