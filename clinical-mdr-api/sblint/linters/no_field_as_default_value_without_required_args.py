#!/usr/bin/env python

import ast
import sys

from rich import print as rptint

from sblint.sblinter import SBLinter


class NoFieldAsDefaultValueWithoutRequiredArgs(SBLinter):
    REQUIRED_ARGS = {"alias", "default", "default_factory"}

    @classmethod
    def validate(cls, code: str):
        """
        Validates the given Python code by checking if it contains any
        `pydantic.Field` that assigned as default value while not providing
        one of the arguments defined in `cls.REQUIRED_ARGS`.

        Args:
            code (str): The Python code to validate.

        Returns:
            bool: `True` if the code doesn't contain improper use of `pydantic.Field`
            as a default value, otherwise `False`.
        """
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for body_item in node.body:
                    if (
                        isinstance(body_item, ast.AnnAssign)
                        and isinstance(body_item.value, ast.Call)
                        and isinstance(body_item.value.func, ast.Name)
                        and body_item.value.func.id == "Field"
                        and not cls.REQUIRED_ARGS.intersection(
                            kw.arg for kw in body_item.value.keywords
                        )
                    ):
                        return False
        return True

    @classmethod
    def expose_validation(cls, invalid_files: list[str]):
        """
        Displays a message indicating that improper use of `pydantic.Field`
        within as a default value.

        Args:
            invalid_files (list[str]): A list of file paths that contain improper use of
            `pydantic.Field` as a default value.
        """
        if invalid_files:
            rptint(
                "In the following files, [b]pydantic.Field[/b] is assigned as a default value "
                "without specifying any of the required arguments: [b]alias[/b], [b]default[/b] or [b]default_factory[/b]."
                "\nEither pass [b]pydantic.Field[/b] to [b]typing.Annotated[/b] "
                "or pass one of the required arguments to [b]pydantic.Field[/b]."
            )

            super().expose_validation(invalid_files)


if __name__ == "__main__":
    NoFieldAsDefaultValueWithoutRequiredArgs.validate_and_report_me(sys.argv[1:])
