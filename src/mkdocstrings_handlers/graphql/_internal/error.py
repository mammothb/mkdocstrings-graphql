import os


class GraphQLFileSyntaxError(Exception):
    def __init__(self, path: str | os.PathLike, message: str):
        super().__init__()
        self.message = self.format_message(path, message)

    def __str__(self) -> str:
        return self.message

    def format_message(self, path: str | os.PathLike, message: str) -> str:
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
