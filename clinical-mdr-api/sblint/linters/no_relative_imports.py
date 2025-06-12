#!/usr/bin/env python

import ast
import sys

from rich import print as rptint

from sblint.sblinter import SBLinter


class NoRelativeImports(SBLinter):
    @classmethod
    def validate(cls, code: str) -> bool:
        """
        Validates the given Python code by checking if it contains any relative imports.

        Args:
            code (str): The Python code to validate.

        Returns:
            bool: True if the code contains relative imports, False otherwise.
        """
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level != 0:
                return False
        return True

    @classmethod
    def expose_validation(cls, invalid_files: list[str]) -> None:
        """
        Displays a message indicating that relative imports should be removed from the specified files.

        Args:
            invalid_files (list[str]): A list of file paths that contain relative imports.
        """
        if invalid_files:
            rptint(
                "The following files contain imports that use relative paths. Use only absolute paths for imports."
            )

            super().expose_validation(invalid_files)


if __name__ == "__main__":
    NoRelativeImports.validate_and_report_me(sys.argv[1:])
