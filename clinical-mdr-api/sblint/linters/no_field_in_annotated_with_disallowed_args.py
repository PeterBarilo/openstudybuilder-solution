#!/usr/bin/env python

import ast
import sys

from rich import print as rptint

from sblint.sblinter import SBLinter


class NoFieldInAnnotatedWithDisallowedArgs(SBLinter):
    DISALLOWED_ARGS = {"alias", "default", "default_factory"}

    @classmethod
    def validate(cls, code: str) -> bool:
        """
        Validates the given Python code by checking if it contains any
        `pydantic.Field` that is passed to `typing.Annotated` while also
        providing one of the arguments defined in `cls.DISALLOWED_ARGS`.

        Args:
            code (str): The Python code to validate.

        Returns:
            bool: `True` if the code doesn't contain improper use of `pydantic.Field`
            within `typing.Annotated`, otherwise `False`.
        """
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for body_item in node.body:
                    if (
                        isinstance(body_item, ast.AnnAssign)
                        and isinstance(body_item.annotation, ast.Subscript)
                        and isinstance(body_item.annotation.slice, ast.Tuple)
                    ):
                        for elts in body_item.annotation.slice.elts:
                            if (
                                isinstance(elts, ast.Call)
                                and isinstance(elts.func, ast.Name)
                                and elts.func.id == "Field"
                                and cls.DISALLOWED_ARGS.intersection(
                                    kw.arg for kw in elts.keywords
                                )
                            ):
                                return False
        return True

    @classmethod
    def expose_validation(cls, invalid_files: list[str]) -> None:
        """
        Displays a message indicating that improper use of `pydantic.Field`
        within `typing.Annotated` should be refactored.

        Args:
            invalid_files (list[str]): A list of file paths that contain improper use of
            `pydantic.Field` within `typing.Annotated`.
        """
        if invalid_files:
            rptint(
                "In the following files, [b]pydantic.Field[/b] is passed to [b]typing.Annotated[/b] "
                "while specifying at least one of the disallowed arguments: [b]alias[/b], [b]default[/b] or [b]default_factory[/b]."
                "\nEither assign [b]pydantic.Field[/b] as the default value "
                "or remove all disallowed arguments from [b]pydantic.Field[/b]."
            )

            super().expose_validation(invalid_files)


if __name__ == "__main__":
    NoFieldInAnnotatedWithDisallowedArgs.validate_and_report_me(sys.argv[1:])
