# adt [![CircleCI](https://circleci.com/gh/jspahrsummers/adt.svg?style=svg&circle-token=2652421c13c636b5da0c992d77ec2fb0b128dd49)](https://circleci.com/gh/jspahrsummers/adt)

`adt` is a library providing [algebraic data types](https://en.wikipedia.org/wiki/Algebraic_data_type) in Python, with a clean, intuitive syntax, and support for [`typing`](https://docs.python.org/3/library/typing.html) through a [mypy plugin](#mypy-plugin).

**Table of contents:**

1. [What are algebraic data types?](#what-are-algebraic-data-types)
    1. [Pattern matching](#pattern-matching)
    1. [Compared to Enums](#compared-to-enums)
    1. [Compared to inheritance](#compared-to-inheritance)
    1. [Examples in other programming languages](#examples-in-other-programming-languages)
1. [Installation](#installation)
    1. [mypy plugin](#mypy-plugin)
1. [Defining an ADT](#defining-an-adt)
    1. [Generated functionality](#generated-functionality)
    1. [Custom methods](#custom-methods)

# What are algebraic data types?

An [algebraic data type](https://en.wikipedia.org/wiki/Algebraic_data_type) (also known as an ADT) is a way to represent multiple variants of a single type, each of which can have some data associated with it. The idea is very similar to [tagged unions and sum types](https://en.wikipedia.org/wiki/Tagged_union), which in Python are represented as [Enums](#compared-to-enums).

ADTs are useful for a variety of data structures, including binary trees:

```python
@adt
class Tree:
    EMPTY: Case
    LEAF: Case[int]
    NODE: Case["Tree", "Tree"]
```

Abstract syntax trees (like you might implement as part of a parser, compiler, or interpreter):

```python
@adt
class Expression:
    LITERAL: Case[float]
    UNARY_MINUS: Case["Expression"]
    ADD: Case["Expression", "Expression"]
    MINUS: Case["Expression", "Expression"]
    MULTIPLY: Case["Expression", "Expression"]
    DIVIDE: Case["Expression", "Expression"]
```

Or more generic versions of a variant type, like an `Either` type that represents a type A or a type B, but not both:

```python
L = TypeVar('L')
R = TypeVar('R')

@adt
class Either(Generic[L, R]):
    LEFT: Case[L]
    RIGHT: Case[R]
```

## Pattern matching

Now, defining a type isn't that interesting by itself. A lot of the expressivity of ADTs arises when you [pattern match](https://en.wikipedia.org/wiki/Pattern_matching) over them (sometimes known as "destructuring").

For example, we could use the `Either` ADT from above to implement a sort of error handling:

```python
# Defined in some other module, perhaps
def some_operation() -> Either[Exception, int]:
    return Either.RIGHT(22)  # Example of building a constructor

# Run some_operation, and handle the success or failure
default_value = 5
unpacked_result = some_operation().match(
    # In this case, we're going to ignore any exception we receive
    left=lambda ex: default_value,
    right=lambda result: result)
```

_Aside: this is very similar to how error handling is implemented in languages like [Haskell](https://www.haskell.org/), because it avoids the unpredictable control flow of raising and catching exceptions, and ensures that callers need to make an explicit decision about what to do in an error case._

One can do the same thing with the `Expression` type above (just more cases to match):

```python
def handle_expression(e: Expression):
    return e.match(
        literal=lambda n: ...,
        unary_minus=lambda expr: ...,
        add=lambda lhs, rhs: ...,
        minus=lambda lhs, rhs: ...,
        multiply=lambda lhs, rhs: ...,
        divide=lambda lhs, rhs: ...)
```

## Compared to Enums

ADTs are somewhat similar to [`Enum`s](https://docs.python.org/3/library/enum.html) from the Python standard library (in fact, the uppercase naming convention is purposely similar).

For example, an `Enum` version of `Expression` might look like:

```python
from enum import Enum, auto
class EnumExpression(Enum):
    LITERAL = auto()
    UNARY_MINUS = auto()
    ADD = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
```

However, this doesn't allow data to be associated with each of these enum values. A particular value of `Expression` will tell you about a _kind_ of expression that exists, but the operands to the expressions still have to be stored elsewhere.

From this perspective, ADTs are like `Enum`s that can optionally have data associated with each case.

## Compared to inheritance

Algebraic data types are a relatively recent introduction to object-oriented programming languages, for the simple reason that inheritance can replicate the same behavior.

Continuing our examples with the `Expression` ADT, here's how one might represent it with inheritance in Python:

```python
from abc import ABC
class ABCExpression(ABC):
    pass

class LiteralExpression(ABCExpression):
    def __init__(self, value: float):
        pass

class UnaryMinusExpression(ABCExpression):
    def __init__(self, inner: ABCExpression):
        pass

class AddExpression(ABCExpression):
    def __init__(self, lhs: ABCExpression, rhs: ABCExpression):
        pass

class MinusExpression(ABCExpression):
    def __init__(self, lhs: ABCExpression, rhs: ABCExpression):
        pass

class MultiplyExpression(ABCExpression):
    def __init__(self, lhs: ABCExpression, rhs: ABCExpression):
        pass

class DivideExpression(ABCExpression):
    def __init__(self, lhs: ABCExpression, rhs: ABCExpression):
        pass
```

This is noticeably more verbose, and the code to consume these types gets much more complex as well:

```python
e: ABCExpression = UnaryMinusExpression(LiteralExpression(3))  # Example of creating an expression

if isinstance(e, LiteralExpression):
    result = ... # do something with e.value
elif isinstance(e, UnaryMinusExpression):
    result = ... # do something with e.inner
elif isinstance(e, AddExpression):
    result = ... # do something with e.lhs and e.rhs
elif isinstance(e, MinusExpression):
    result = ... # do something with e.lhs and e.rhs
elif isinstance(e, MultiplyExpression):
    result = ... # do something with e.lhs and e.rhs
elif isinstance(e, DivideExpression):
    result = ... # do something with e.lhs and e.rhs
else:
    raise ValueError(f'Unexpected type of expression: {e}')
```

ADTs offer a simple way to define a type which is _one of a set of possible cases_, and allowing data to be associated with each case and packed/unpacked along with it.

## Examples in other programming languages

Algebraic data types are very common in functional programming languages, like [Haskell](https://www.haskell.org/) or [Scala](https://www.scala-lang.org/), but they're gaining increasing acceptance in "mainstream" programming languages as well.

Here are a few examples.

### [Rust](https://www.rust-lang.org/)

Rust `enum`s are actually full-fledged ADTs. Here's how an `Either` ADT could be defined:

```rust
enum Either<L, R> {
    Left(L),
    Right(R),
}
```

### [Swift](https://developer.apple.com/swift/)

[Swift enumerations](https://docs.swift.org/swift-book/LanguageGuide/Enumerations.html) are very similar to Rust's, and behave like algebraic data types through their support of "associated values."

```swift
enum Either<L, R> {
    case Left(L)
    case Right(R)
}
```

### [TypeScript](https://en.wikipedia.org/wiki/Microsoft_TypeScript)

[TypeScript](https://en.wikipedia.org/wiki/Microsoft_TypeScript) offers ADTs through a language feature known as ["discriminated unions"](https://www.typescriptlang.org/docs/handbook/advanced-types.html#discriminated-unions).

See this example from their documentation:

```typescript
interface Square {
    kind: "square";
    size: number;
}
interface Rectangle {
    kind: "rectangle";
    width: number;
    height: number;
}
interface Circle {
    kind: "circle";
    radius: number;
}

type Shape = Square | Rectangle | Circle;
```

# Installation

To add `adt` as a library in your Python project, simply run `pip` (or `pip3`, as it may be named on your system):

```
pip install algebraic-data-types
```

This will install [the latest version from PyPI](https://pypi.org/project/algebraic-data-types/).

## mypy plugin

The library also comes with a plugin for [mypy](http://mypy-lang.org/) that enables typechecking of `@adt` definitions. **If you are already using mypy, the plugin is required to avoid nonsensical type errors.**

To enable the `adt` typechecking plugin, add the following to a `mypy.ini` file in your project's working directory:

```
[mypy]
plugins = adt.mypy_plugin
```

# Defining an ADT

To begin defining your own data type, import the `@adt` decorator and `Case[…]` annotation:

[//]: # (README_TEST:AT_TOP)
```python
from adt import adt, Case
```

Then, define a new Python class, upon which you apply the `@adt` decorator:

```python
@adt
class MyADT1:
    pass
```

For each case (variant) that your ADT will have, declare a field with the `Case` annotation. It's conventional to declare your fields with ALL_UPPERCASE names, but the only true restriction is that they _cannot_ be lowercase.

```python
@adt
class MyADT2:
    FIRST_CASE: Case
    SECOND_CASE: Case
```

If you want to associate some data with a particular case, list the type of that data in brackets after `Case` (similar to the `Generic[…]` and `Tuple[…]` annotations from `typing`). For example, to add a case with an associated string:

```python
@adt
class MyADT3:
    FIRST_CASE: Case
    SECOND_CASE: Case
    STRING_CASE: Case[str]
```

You can build cases with arbitrarily many associated pieces of data, as long as all the types are listed:

```python
@adt
class MyADT4:
    FIRST_CASE: Case
    SECOND_CASE: Case
    STRING_CASE: Case[str]
    LOTS_OF_DATA_CASE: Case[int, str, str, Dict[int, int]]
```

ADTs can also be recursive—i.e., an ADT can itself be stored alongside a specific case—though the class name has to be provided in double quotes (a restriction which also applies to `typing`).

A typical example of a recursive ADT is a linked list. Here, the list is also made generic over a type `T`:

```python
T = TypeVar('T')

@adt
class LinkedList(Generic[T]):
    NIL: Case
    CONS: Case[T, "LinkedList[T]"]
```

See the library's [tests](tests/) for more examples of complete ADT definitions.

## Generated functionality

Given an ADT defined as follows:

```python
@adt
class MyADT5:
    EMPTY: Case
    INTEGER: Case[int]
    STRING_PAIR: Case[str, str]
```

The `@adt` decorator will automatically generate accessor methods of the following form:

```python
    def empty(self) -> None:
        return None

    def integer(self) -> int:
        ... # unpacks int value and returns it

    def string_pair(self) -> Tuple[str, str]:
        ... # unpacks strings and returns them in a tuple
```

These accessors can be used to obtain the data associated with the ADT case, but **accessors will throw an exception if the ADT was not constructed with the matching case**. This is a shorthand when you already know the case of an ADT object.

`@adt` will also automatically generate a pattern-matching method, which can be used when you _don't_ know which case you have ahead of time:

[//]: # (README_TEST:IGNORE)
```python
    Result = TypeVar('Result')
    
    def match(self,
              empty: Callable[[], Result],
              integer: Callable[[int], Result],
              string_pair: Callable[[str, str], Result]) -> Result:
        if ... self was constructed as EMPTY ...:
            return empty()
        elif ... self was constructed as INTEGER ...:
            return integer(self.integer())
        elif ... self was constructed as STRING_PAIR ...:
            return string_pair(*self.string_pair())
        
        # if pattern match is incomplete, an exception is raised
```

See the library's [tests](tests/) for examples of using these generated methods.

`@adt` will also generate `__repr__`, `__str__`, and `__eq__` methods (only if they are not [defined already](#custom-methods)), to make ADTs convenient to use by default.

## Custom methods

Arbitrary methods can be defined on ADTs by simply including them in the class definition as normal.

For example, to build "safe" versions of the default accessors on `ExampleADT`, which return `None` instead of throwing an exception when the case is incorrect:

```python
@adt
class ExampleADT:
    EMPTY: Case
    INTEGER: Case[int]
    STRING_PAIR: Case[str, str]

    @property
    def safe_integer(self) -> Optional[int]:
        return self.match(empty=lambda: None,
                          integer=lambda n: n,
                          string_pair=lambda _a, _b: None)

    @property
    def safe_string_pair(self) -> Optional[Tuple[str, str]]:
        return self.match(empty=lambda: None,
                          integer=lambda: None,
                          string_pair=lambda a, b: tuple(a, b))
```

However, additional fields _must not_ be added to the class, as the decorator will attempt to interpret them as ADT `Case`s (which will fail).