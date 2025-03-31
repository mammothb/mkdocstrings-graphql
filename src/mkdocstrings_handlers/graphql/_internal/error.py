from __future__ import annotations

import sys
from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from pathlib import Path

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override  # pyright:ignore[reportUnreachable]


@final
class GraphQLFileSyntaxError(Exception):
    def __init__(self, path: str | Path, message: str):
        super().__init__()
        self.message = self.format_message(path, message)

    @override
    def __str__(self) -> str:
        return self.message

    def format_message(self, path: str | Path, message: str) -> str:
        """Builds final error message from path to schema file and error
        message.

        Args:
            path: A `str` or `PathLike` object pointing to a file that failed
                to validate.
            message: A `str` with validation message.

        Returns:
            Final error message.
        """
        return f"Could not load {path}:\n{message}"
