# adt [![CircleCI](https://circleci.com/gh/jspahrsummers/adt.svg?style=svg&circle-token=2652421c13c636b5da0c992d77ec2fb0b128dd49)](https://circleci.com/gh/jspahrsummers/adt)

Algebraic data types for Python.

See [the tests](tests/) for example usage.

## Setting up mypy plugin

To typecheck your usages of `@adt`, add the following to a `mypy.ini` file in your project's working directory:

```
[mypy]
plugins = adt.mypy_plugin
```
