from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mkdocstrings_handlers.graphql._internal.models import Schema


class SchemasCollection:
    is_collection: bool = True

    def __init__(self) -> None:
        self.members: dict[str, Schema] = {}

    def __bool__(self) -> bool:
        return True

    def __contains__(self, item: Any) -> bool:
        return item in self.members

    def __getitem__(self, key: Any) -> Schema:
        return self.members[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        self.members[key] = value

    @property
    def all_members(self) -> dict[str, Schema]:
        return self.members
