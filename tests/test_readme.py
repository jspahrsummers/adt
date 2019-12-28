import unittest


class TestMyPyPlugin(unittest.TestCase):
    def test_readmeExamplesAreExecutable(self) -> None:
        """Run a module that uses the examples from the README to test if they execute successfully."""
        from .source_files import readme_examples
