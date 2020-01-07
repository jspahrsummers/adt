import unittest
import mypy.main
import mypy.version
import os
import sys


class TestMyPyPlugin(unittest.TestCase):
    def test_issue21(self) -> None:
        self._call_mypy_on_source_file("issue21.py")

    @unittest.expectedFailure  # Issue #26 is still unfixed
    def test_issue25(self) -> None:
        # Activate it when working on it.
        # cf. https://github.com/jspahrsummers/adt/issues/25
        self._call_mypy_on_source_file("issue25.py")

    @unittest.expectedFailure  # Issue #26 is still unfixed
    def test_issue26(self) -> None:
        # Activate it when working on it.
        # cf. https://github.com/jspahrsummers/adt/issues/26
        self._call_mypy_on_source_file("issue26.py")

    @unittest.expectedFailure  # Fails because issue #26 is still unfixed
    def test_readme_examples(self) -> None:
        self._call_mypy_on_source_file("readme_examples.py")

    def _call_mypy_on_source_file(self, source_file_name: str) -> None:
        print(
            f"Testing {source_file_name} with mypy=={mypy.version.__version__}"
        )
        self._call_mypy_on_path(
            os.path.join(os.path.dirname(__file__), "source_files",
                         source_file_name))

    def _call_mypy_on_path(self, testfile: str) -> None:
        try:
            mypy.main.main(None, sys.stdout, sys.stderr, args=[testfile])
        except SystemExit:
            self.fail(msg="Error during type-check")
