from __future__ import annotations

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


class DocstringEnumValue(DocstringNamedElement):
    pass


class DocstringField(DocstringNamedElement):
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
        self, value: list[DocstringArgument], title: str | None = None
    ) -> None:
        super().__init__(title)
        self.value: list[DocstringArgument] = value


class DocstringSectionEnumValues(DocstringSection):
    kind: ClassVar[DocstringSectionKind] = DocstringSectionKind.ENUM_VALUES

    def __init__(
        self, value: list[DocstringEnumValue], title: str | None = None
    ) -> None:
        super().__init__(title)
        self.value: list[DocstringEnumValue] = value


class DocstringSectionFields(DocstringSection):
    kind: ClassVar[DocstringSectionKind] = DocstringSectionKind.FIELDS

    def __init__(self, value: list[DocstringField], title: str | None = None) -> None:
        super().__init__(title)
        self.value: list[DocstringField] = value


class DocstringSectionReturns(DocstringSection):
    kind: ClassVar[DocstringSectionKind] = DocstringSectionKind.RETURNS

    def __init__(self, value: list[DocstringReturn], title: str | None = None) -> None:
        super().__init__(title)
        self.value: list[DocstringReturn] = value


class DocstringSectionText(DocstringSection):
    kind: ClassVar[DocstringSectionKind] = DocstringSectionKind.TEXT

    def __init__(self, value: str, title: str | None = None) -> None:
        super().__init__(title)
        self.value: str = value
