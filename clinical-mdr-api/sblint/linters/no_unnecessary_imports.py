#!/usr/bin/env python

import ast
import sys

from rich import print as rptint
from rich.table import Table

from sblint.sblinter import SBLinter


class NoUnnecessaryImports(SBLinter):
    UNNECESSARY_IMPORTS = [
        ("typing", "Optional", "x | None"),
        ("typing", "Union", "x | y"),
        ("typing", "List", "list"),
        ("typing", "Set", "set"),
        ("typing", "Dict", "dict"),
        ("typing", "Tuple", "tuple"),
    ]

    @classmethod
    def validate(cls, code: str) -> bool:
        """
        Validates the given Python code by checking if it contains any
        imports that are deemed unnecessary based on the `cls.UNNECESSARY_IMPORTS`
        The `UNNECESSARY_IMPORTS` attribute is expected to be a collection of tuples
        where each tuple contains, in order, a module name, an import name and an alternative.

        Args:
            code (str): The Python code to be validated.

        Returns:
            bool: `True` if the code doesn't contain unnecessary imports, otherwise `False`.
        """
        MODULES = {x[0] for x in cls.UNNECESSARY_IMPORTS}
        IMPORTS = {x[1] for x in cls.UNNECESSARY_IMPORTS}

        tree = ast.parse(code)

        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module in MODULES
                and any(alias.name in IMPORTS for alias in node.names)
            ) or (
                isinstance(node, ast.Import)
                and any(alias.name in IMPORTS for alias in node.names)
            ):
                return False
        return True

    @classmethod
    def expose_validation(cls, invalid_files: list[str]) -> None:
        """
        Displays a message indicating that unnecessary imports should be removed
        from the specified files and suggests alternatives. It also displays a
        formatted table of modules, unnecessary imports, and their alternatives.

        Args:
            invalid_files (list[str]): A list of file paths that contain unnecessary imports.
        """
        if invalid_files:
            print(
                "The following files contain unnecessary imports. Remove them and use their alternatives:"
            )

            table = Table()

            table.add_column("Module", style="cyan")
            table.add_column("Import", style="red")
            table.add_column("Alternative", style="green")

            for module, unnecessary, alternative in cls.UNNECESSARY_IMPORTS:
                table.add_row(
                    module, f":x: {unnecessary}", f":white_check_mark: {alternative}"
                )

            rptint(table)

            super().expose_validation(invalid_files)


if __name__ == "__main__":
    NoUnnecessaryImports.validate_and_report_me(sys.argv[1:])
