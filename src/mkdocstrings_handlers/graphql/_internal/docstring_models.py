from typing import Any, ClassVar

from mkdocstrings_handlers.graphql._internal.enum import DocstringSectionKind


class DocstringElement:
    def __init__(self, *, description: str, annotation: str | None = None) -> None:
        self.description: str = description
        self.annotation: str | None = annotation


class DocstringNamedElement(DocstringElement):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        annotation: str | None = None,
        value: str | None = None,
    ) -> None:
        super().__init__(description=description, annotation=annotation)
        self.name: str = name
        self.value: str | None = value


class DocstringArgument(DocstringNamedElement):
    pass


class DocstringReturn(DocstringElement):
    pass


class DocstringSection:
    kind: ClassVar[DocstringSectionKind]

    def __init__(self, title: str | None = None) -> None:
        self.title: str | None = title
        self.value: Any = None

    def __bool__(self) -> bool:
        return bool(self.value)


class DocstringSectionArguments(DocstringSection):
    kind: ClassVar[DocstringSectionKind] = DocstringSectionKind.ARGUMENTS

    def __init__(
        self, *args: Any, value: list[DocstringArgument], **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.value: list[DocstringArgument] = value


class DocstringSectionReturns(DocstringSection):
    kind: ClassVar[DocstringSectionKind] = DocstringSectionKind.RETURNS

    def __init__(self, *args: Any, value: list[DocstringReturn], **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.value: list[DocstringReturn] = value
