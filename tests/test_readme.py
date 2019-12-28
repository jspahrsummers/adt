"""
This test parses the README.md file and extracts all python clode blocks marked with ```python. The code
blocks are then tested for executability.

There is some custom syntax for this test to be minimally invasive to the README.md format:
[//]: # (README_TEST:...)

This syntax is a comment in markdown and allows a block to be decorated with a special meaning for this test.
[//]: # (README_TEST:IGNORE)  --  The clode block will not be included in the test
[//]: # (README_TEST:AT_TOP)  --  The clode block will be executed before all others (useful for imports)
"""
import itertools
import os
import sys
import unittest
from typing import List, Iterable

from tests import helpers

_GENERATED_CODE_FILE_PATH = os.path.join(helpers.PATH_TO_TEST_BASE_DIRECTORY,
                                         "source_files",
                                         "_generated_readme_code.py")

IGNORE_BLOCK_DECORATOR = '[//]: # (README_TEST:IGNORE)'
AT_TOP_BLOCK_DECORATOR = '[//]: # (README_TEST:AT_TOP)'

_IMPLICIT_README_IMPORTS = """
from typing import Dict, Generic, List, Optional, TypeVar, Tuple, Union
"""


def extract_code_from_readme() -> str:
    with open(
            os.path.join(helpers.PATH_TO_TEST_BASE_DIRECTORY, "..",
                         "README.md")) as readme_file_handler:
        return _IMPLICIT_README_IMPORTS + _code_blocks_to_str(
            _extract_code_blocks_from_file(lines=readme_file_handler))


def _extract_code_blocks_from_file(lines: Iterable[str]) -> List[List[str]]:
    """Parse the README.md"""
    code_blocks: List[List[str]] = []
    is_in_code_block = False
    current_code_block: List[str] = []
    ignore_next_code_block = False
    push_next_block_to_top = False

    for line in lines:
        if not is_in_code_block and line.startswith('```python'):
            is_in_code_block = True
            continue
        if not is_in_code_block and line.startswith(IGNORE_BLOCK_DECORATOR):
            ignore_next_code_block = True
            continue
        if not is_in_code_block and line.startswith(AT_TOP_BLOCK_DECORATOR):
            push_next_block_to_top = True
            continue

        if is_in_code_block and line.startswith('```'):
            # End of code block. (Mabye) push it to the block list
            if not ignore_next_code_block:
                if push_next_block_to_top:
                    code_blocks.insert(0, current_code_block)
                else:
                    code_blocks.append(current_code_block)

            current_code_block = []
            is_in_code_block = False
            ignore_next_code_block = False
            push_next_block_to_top = False
            continue

        if is_in_code_block:
            current_code_block.append(line)

    return code_blocks


def _code_blocks_to_str(code_blocks: Iterable[Iterable[str]]) -> str:
    return "".join(itertools.chain.from_iterable(code_blocks))


class TestMyPyPlugin(unittest.TestCase):
    def test_readmeExamplesAreExecutable(self) -> None:
        """Executing the code blocks given in the README.md"""
        temporary_code = extract_code_from_readme()
        globals_for_exec = {"__name__": "README.md"}

        try:
            exec(temporary_code, globals_for_exec)
        except Exception:
            print(">>> Found error in generated readme code file",
                  file=sys.stderr)
            print(temporary_code, file=sys.stderr)
            raise
