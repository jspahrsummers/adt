# mypy: no-warn-redundant-casts
import itertools
from decimal import Decimal
from typing import Optional, Callable, List, Type, Any, Iterable, Union
import typing

import mypy.types
import mypy.typevars
from mypy.nodes import (
    ARG_NAMED,
    ARG_POS,
    MDEF,
    Argument,
    AssignmentStmt,
    Block,
    FuncDef,
    FuncBase,
    NameExpr,
    PassStmt,
    PlaceholderNode,
    SymbolTableNode,
    SymbolNode,
    TypeVarExpr,
    Var,
)
from mypy.plugin import AnalyzeTypeContext, TypeAnalyzerPluginInterface, ClassDefContext, Plugin
from mypy.semanal import set_callable_name
from mypy.typevars import fill_typevars
from mypy.util import get_unique_redefinition_name


def plugin(version: str) -> Type[Plugin]:
    """Return plugin class depending on mypy version."""
    raw_version = version.split("+", 1)[0]  # Handle development versions
    assert Decimal(raw_version) >= Decimal("0.711")
    return ADTPlugin


# fullname and name became properties with https://github.com/python/mypy/pull/7829
# These are compatibility shims
def get_fullname(x: Union[FuncBase, SymbolNode]) -> str:
    fn = x.fullname
    if callable(fn):
        return typing.cast(str, fn())
    return typing.cast(str, fn)


def get_name(x: Union[FuncBase, SymbolNode]) -> str:
    fn = x.name
    if callable(fn):
        return typing.cast(str, fn())
    return fn


class ADTPlugin(Plugin):
    # Fully-qualified name for @adt
    _ADT_DECORATOR = 'adt.decorator.adt'

    def get_type_analyze_hook(
            self, fullname: str
    ) -> Optional[Callable[[AnalyzeTypeContext], mypy.types.Type]]:
        if fullname == "adt.case.Case":
            return _convert_case_type
        return None

    def get_class_decorator_hook(
            self,
            fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        if fullname != self._ADT_DECORATOR:
            return None

        return _transform_class


def _convert_case_type(type_context: AnalyzeTypeContext) -> mypy.types.Type:
    """Convert Case[..] type to CaseConstructor[..]"""
    # We do this because the semantic analyzer runs before the class_decorator_hook
    # gets a chance to remove the Cases. This will convert the type into a valid
    # runtime type and allows the class_decorator hook to be executed. The hook
    # then removes this type from the ADT completely.
    api: TypeAnalyzerPluginInterface = type_context.api
    type_to_convert: mypy.types.UnboundType = type_context.type

    call_args = type_to_convert.args
    function_type = type_context.api.named_type("builtins.function", [])

    arg_types = list(map(api.analyze_type, call_args))
    arg_kinds = [mypy.types.ARG_POS for _ in call_args]
    arg_names = [None for _ in call_args]

    return_type = api.named_type("adt.CaseConstructor", arg_types)

    return mypy.types.CallableType(
        arg_types=arg_types,
        arg_kinds=arg_kinds,
        arg_names=arg_names,
        ret_type=return_type,
        fallback=function_type,
    )


class _CaseDef:
    context: ClassDefContext
    name: str
    types: List[mypy.types.Type]

    def __init__(self, context: ClassDefContext, name: str,
                 types: List[mypy.types.Type]):
        self.context = context
        self.name = name
        self.types = self._normalize_types(types)
        super().__init__()

    @staticmethod
    def _normalize_types(types: List[mypy.types.Type]
                         ) -> List[mypy.types.Type]:
        if len(types) != 1:
            return types

        t = types[0]

        # Explode tuples and replace None with an empty list if it's the only
        # thing provided
        if isinstance(t, mypy.types.TupleType):
            return t.items
        elif isinstance(t, mypy.types.NoneType):
            return []
        else:
            return types

    def constructor_args(self) -> List[Argument]:
        return [
            Argument(variable=Var(f'_{i}', t),
                     type_annotation=t,
                     initializer=None,
                     kind=ARG_POS) for i, t in enumerate(self.types)
        ]

    def accessor_return(self) -> mypy.types.Type:
        if len(self.types) == 0:
            return mypy.types.NoneType()
        elif len(self.types) == 1:
            return self.types[0]
        else:
            return mypy.types.TupleType(
                self.types, self.context.api.named_type('__builtins__.tuple'))

    def match_lambda(self,
                     return_type: mypy.types.Type) -> mypy.types.CallableType:
        argKinds = list(itertools.repeat(ARG_POS, len(self.types)))
        argNames = list(itertools.repeat(None, len(self.types)))

        return mypy.types.CallableType(
            self.types, argKinds, argNames, return_type,
            self.context.api.named_type('__builtins__.function'))

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, _CaseDef):
            return False

        return self.name == other.name and self.types == other.types

    def __repr__(self) -> str:
        return f'_CaseDef(name={self.name}, types={self.types!r})'

    def __str__(self) -> str:
        typeStr = ", ".join((str(t) for t in self.types))
        return f'{self.name}: Case[{typeStr}]'


def _transform_class(context: ClassDefContext) -> None:
    cls = context.cls

    instanceType = fill_typevars(cls.info)
    assert isinstance(instanceType, mypy.types.Instance)

    cases = _get_and_delete_cases(context)
    if cases is None:  # Cases were not successfully deleted. We need to defer
        context.api.defer()
        return

    for case in cases:
        _add_constructor_for_case(context, case, selfType=instanceType)
        _add_accessor_for_case(context, case)

    _add_match(context, cases)


# Returns ADT cases which were listed as class variables (similar to
# cls.__annotations__ at runtime), and removes those variables from
# typechecking, as they will be replaced by constructor methods.
def _get_and_delete_cases(context: ClassDefContext
                          ) -> Optional[List[_CaseDef]]:
    """Search the class body for adt's Case constructions and delete them

    For a given context, search the class body for assignments of the form
    `CASENAME: Case[...]`. Delete them, and return a _CaseDef for each.

    In case the body is not ready (because the semantic analyzer included a
    PlaceHolder expression), this function will return None and is expected
    to be called again.

    If no PlaceHolder is found, return a list of _CaseDef.
    """
    cls = context.cls

    caseDefs: List[_CaseDef] = []
    removed: List[int] = []
    for i, statement in enumerate(cls.defs.body):
        # Any assignment that doesn't use the new type declaration
        # syntax can be ignored out of hand.
        if not (isinstance(statement, AssignmentStmt)
                and statement.new_syntax):
            continue

        # a: int, b: str = 1, 'foo' is not supported syntax so we
        # don't have to worry about it.
        lval = statement.lvalues[0]
        if not isinstance(lval, NameExpr):
            continue

        sym = cls.info.names.get(lval.name)
        if sym is None:
            # This name is likely blocked by a star import. We don't need to defer because
            # defer() is already called by mark_incomplete().
            continue

        var = sym.node
        if isinstance(var, PlaceholderNode):
            # This node is not ready yet.
            return None

        assert isinstance(var, Var)
        assert isinstance(var.type, mypy.types.CallableType)
        assert isinstance(var.type.ret_type, mypy.types.Instance)
        assert get_fullname(
            var.type.ret_type.type) == "adt.case.CaseConstructor"

        caseDefs.append(
            _CaseDef(context=context,
                     name=get_name(var),
                     types=var.type.ret_type.args))
        removed.append(i)

    for i in reversed(removed):
        del cls.defs.body[i]

    return caseDefs


# Class constructor method per case (uppercase)
def _add_constructor_for_case(context: ClassDefContext, case: _CaseDef,
                              selfType: mypy.types.Instance) -> None:
    _add_method(context,
                name=case.name,
                args=case.constructor_args(),
                return_type=selfType,
                is_classmethod=True)


# Accessor method per case (lowercase)
def _add_accessor_for_case(context: ClassDefContext, case: _CaseDef) -> None:
    _add_method(context,
                name=case.name.lower(),
                args=[],
                return_type=case.accessor_return())


# `match` method for pattern matching (uses lowercase case names)
def _add_match(context: ClassDefContext, cases: Iterable[_CaseDef]) -> None:
    matchResultType = _add_typevar(context, '_MatchResult')

    caseCallables = {
        case: _callable_type_for_adt_case(context,
                                          case,
                                          resultType=matchResultType)
        for case in cases
    }

    matchArgs = [
        Argument(variable=Var(case.name.lower(), callableType),
                 type_annotation=callableType,
                 initializer=None,
                 kind=ARG_NAMED)
        for case, callableType in caseCallables.items()
    ]

    _add_method(context,
                name='match',
                args=matchArgs,
                return_type=mypy.types.TypeVarType(matchResultType),
                tvar_def=matchResultType)


# Generates a new, unique, unbounded type variable and defines it within the
# body of the given class.
def _add_typevar(context: ClassDefContext,
                 tVarName: str) -> mypy.types.TypeVarDef:
    typeInfo = context.cls.info
    tVarQualifiedName = f'{get_fullname(typeInfo)}.{tVarName}'
    objectType = context.api.named_type('__builtins__.object')

    tVarExpr = TypeVarExpr(tVarName, tVarQualifiedName, [], objectType)
    typeInfo.names[tVarName] = SymbolTableNode(MDEF, tVarExpr)

    return mypy.types.TypeVarDef(tVarName, tVarQualifiedName, -1, [],
                                 objectType)


# Determines the Callable type appropriate for destructuring the ADT case
# described by `case`.
def _callable_type_for_adt_case(context: ClassDefContext, case: _CaseDef,
                                resultType: mypy.types.TypeVarDef
                                ) -> mypy.types.CallableType:
    callableType = case.match_lambda(
        return_type=mypy.types.TypeVarType(resultType))
    callableType.variables = [resultType]
    return callableType


# This is mypy.plugins.common.add_method() extended to support class methods.
#
# See original code at https://github.com/python/mypy/blob/17b68c6b7eaa76853422544e32b1d6c5c3acc55a/mypy/plugins/common.py#L81,
# and license at https://github.com/python/mypy/blob/17b68c6b7eaa76853422544e32b1d6c5c3acc55a/LICENSE.
def _add_method(
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
            mypy.types.AnyType(mypy.types.TypeOfAny.implementation_artifact),
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
        arg_names.append(get_name(arg.variable))
        arg_kinds.append(arg.kind)

    signature = mypy.types.CallableType(arg_types, arg_kinds, arg_names,
                                        return_type, function_type)
    if tvar_def:
        signature.variables = [tvar_def]

    func = FuncDef(name, args, Block([PassStmt()]))
    func.info = info
    func.is_class = is_classmethod
    func.type = set_callable_name(signature, func)
    func._fullname = get_fullname(info) + '.' + name
    func.line = info.line

    # NOTE: we would like the plugin generated node to dominate, but we still
    # need to keep any existing definitions so they get semantically analyzed.
    if name in info.names:
        # Get a nice unique name instead.
        r_name = get_unique_redefinition_name(name, info.names)
        info.names[r_name] = info.names[name]

    info.defn.defs.body.append(func)
    info.names[name] = SymbolTableNode(MDEF, func, plugin_generated=True)
