# Configuration and options dataclasses.

from __future__ import annotations

import sys
from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING, Any

from mkdocstrings import get_logger

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self  # pyright:ignore[reportUnreachable]


_logger = get_logger(__name__)


if TYPE_CHECKING:
    from collections.abc import MutableMapping


_dataclass_options = {"frozen": True}
if sys.version_info >= (3, 10):
    _dataclass_options["kw_only"] = True


@dataclass(**_dataclass_options)
class GraphQLOptions:
    """Available configuration options.

    Attributes:
        heading: (Heading) A custom string to override the autogenerated
            heading of the root object.
        heading_level: (Heading) The initial heading level to use.
        kind: (General) Render all objects of this kind when rendering a
            wildcard directive.
        show_node_full_path: (Docstrings) Show the full path of every node.
        show_root_full_path: (Docstrings) Show the full path for the root
            object heading.
        show_root_members_full_path: (Heading) Show the full path of the root
            members.
        show_root_toc_entry: (Heading) If the root heading is not shown, at
            least add a ToC entry for it.
        show_signature: (Signatures) Whether to render operation signature.
        signature_crossrefs: (Signatures) Whether to render cross-references
            for type annotations in signatures.
        toc_label: (Heading) A custom string to override the autogenerated ToC
            label of the root object.
    """

    heading: str = field(default="")
    heading_level: int = field(default=2)
    kind: str | None = field(default=None)
    show_node_full_path: bool = field(default=False)
    show_root_full_path: bool = field(default=True)
    show_root_members_full_path: bool = field(default=False)
    show_root_toc_entry: bool = field(default=True)
    show_signature: bool = field(default=False)
    signature_crossrefs: bool = field(default=False)
    toc_label: str = field(default="")

    @classmethod
    def coerce(cls, **data: Any) -> MutableMapping[str, Any]:
        """Coerce data."""
        return data

    @classmethod
    def from_data(cls, **data: Any) -> Self:
        """Create an instance from a dictionary."""
        return cls(**cls.coerce(**data))


@dataclass(**_dataclass_options)
class GraphQLConfig:
    """GraphQL handler configuration.

    Attributes:
        schemas: Mapping of schema name to paths which make up the schema.
        handler_options: Configuration options for collecting and rendering
            objects. Post-initialized from ``options`` if provided.
    """

    schemas: dict[str, list[str]] = field(default_factory=dict)
    options: InitVar[dict[str, Any] | None] = field(default=None)
    handler_options: GraphQLOptions = field(init=False)

    def __post_init__(self, options: dict[str, Any] | None) -> None:
        object.__setattr__(self, "handler_options", GraphQLOptions(**(options or {})))

    @classmethod
    def coerce(cls, **data: Any) -> MutableMapping[str, Any]:
        """Coerce data."""
        return data

    @classmethod
    def from_data(cls, **data: Any) -> Self:
        """Create an instance from a dictionary."""
        return cls(**cls.coerce(**data))
