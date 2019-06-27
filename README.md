# adt

Algebraic data types for Python.

See [the tests](tests/test_adt.py) for example usage.

## Setting up mypy plugin

To typecheck your usages of `@adt`, add the following to a `mypy.ini` file in your project's working directory:

```
[mypy]
plugins = adt.mypy_plugin
```
