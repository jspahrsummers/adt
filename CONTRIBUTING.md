# How to contribute

Thanks for wanting to contribute to this project!

## Setting up your environment

The included bootstrap script will set up a Python virtual environment and install the necessary dependencies:

```
script/bootstrap
```

After bootstrapping, confirm that the environment works by running the included test suite:

```
script/test
```

## Issues

Bug reports and enhancement requests are more than welcome. However, if you're able to, a [pull request](#pull-requests) is much better!

## Pull requests

This project uses [CircleCI](https://circleci.com/gh/jspahrsummers/adt/tree/master) for continuous integration, including on pull requests, so most code problems will be caught automatically.

### Testing

To test your changes locally before pushing, please run `script/test` from the command line.

If you are adding new functionality or fixing a bug, please write a test _before_ making the change, verify that it fails, and then ensure that it passes after your changes are applied.

### Code formatting

This project's code is automatically formatted, to ensure a consistent code style without nitpicky reviews or flame wars. Please run `script/reformat --in-place` to format your code changes before submitting them.
