import os
import sys
import unittest

import mypy.main
import mypy.version

from tests import helpers
from tests.test_readme import extract_code_from_readme


class TestMyPyPlugin(unittest.TestCase):
    def test_issue21(self) -> None:
        self._call_mypy_on_source_file("issue21.py")

    @unittest.expectedFailure  # Issue #25 is still unfixed
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
        readme_code = extract_code_from_readme()

        try:
            mypy.main.main(script_path=None,
                           stdout=sys.stdout,
                           stderr=sys.stderr,
                           args=[
                               "-c",
                               readme_code,
                           ])
        except SystemExit:
            self.fail(msg="Error during type-check of readme-code")

    def _call_mypy_on_source_file(self, source_file_name: str) -> None:
        print(
            f"Testing {source_file_name} with mypy=={mypy.version.__version__}"
        )
        self._call_mypy_on_path(
            os.path.join(helpers.PATH_TO_TEST_BASE_DIRECTORY, "source_files",
                         source_file_name))

    def _call_mypy_on_path(self, testfile: str) -> None:
        try:
            mypy.main.main(None, sys.stdout, sys.stderr, args=[testfile])
        except SystemExit:
            self.fail(msg="Error during type-check")
