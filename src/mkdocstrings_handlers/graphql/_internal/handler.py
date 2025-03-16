from __future__ import annotations

import glob
from contextlib import chdir
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from mkdocs.exceptions import PluginError
from mkdocstrings import BaseHandler, CollectionError, CollectorItem, get_logger

from mkdocstrings_handlers.graphql._internal import render
from mkdocstrings_handlers.graphql._internal.collections import SchemasCollection
from mkdocstrings_handlers.graphql._internal.config import GraphQLConfig, GraphQLOptions
from mkdocstrings_handlers.graphql._internal.loader import Loader

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping

    from mkdocs.config.defaults import MkDocsConfig
    from mkdocstrings import HandlerOptions

    from mkdocstrings_handlers.graphql._internal.models import SchemaName


_logger = get_logger(__name__)


class GraphQLHandler(BaseHandler):
    """The GraphQL handler class."""

    name: ClassVar[str] = "graphql"
    """The handler's name."""
    domain: ClassVar[str] = "graphql"
    """The cross-documentation domain/language for this handler."""
    enable_inventory: ClassVar[bool] = False
    """Whether this handler is interested in enabling the creation of the `objects.inv` Sphinx inventory file."""
    fallback_theme: ClassVar[str] = "material"
    """The theme to fallback to."""

    def __init__(self, config: GraphQLConfig, base_dir: Path, **kwargs: Any) -> None:
        """Initialize the handler.

        Parameters:
            config: The handler configuration.
            base_dir: The base directory of the project.
            **kwargs: Arguments passed to the parent constructor.
        """
        super().__init__(**kwargs)

        self.config = config
        self.base_dir = base_dir
        self.global_options = config.options

        schemas = config.schemas or {}
        with chdir(str(self.base_dir)):
            resolved_schemas = {}
            for name, paths in schemas.items():
                resolved_schemas[name] = []
                for path in paths:
                    resolved_schemas[name].extend(glob.glob(path))

        self._schema_to_paths: dict[SchemaName, list[str]] = resolved_schemas
        self._schemas_collection: SchemasCollection = SchemasCollection()

        self._collected: dict[str, CollectorItem] = {}

    def get_options(self, local_options: Mapping[str, Any]) -> HandlerOptions:
        """Get combined default, global and local options.

        Arguments:
            local_options: The local options.

        Returns:
            The combined options.
        """
        extra = {
            **self.global_options.get("extra", {}),
            **local_options.get("extra", {}),
        }
        options = {**self.global_options, **local_options, "extra": extra}
        try:
            return GraphQLOptions.from_data(**options)
        except Exception as error:
            raise PluginError(f"Invalid options: {error}") from error

    def collect(self, identifier: str, _options: GraphQLOptions) -> CollectorItem:
        """Collect data given an identifier and selection configuration.

        Args:
            identifier: The identifier of the object to collect.
            options: The options to use for the collection.

        Returns:
            The collected item.
        """
        if not identifier:
            raise CollectionError("Empty identifier")
        schema_name, member_path = identifier.split(".", 1)
        unknown_schema = schema_name not in self._schemas_collection
        if unknown_schema:
            loader = Loader(
                schema_paths=self._schema_to_paths[schema_name],
                schemas_collection=self._schemas_collection,
            )
            loader.load(schema_name)
        return self._schemas_collection[schema_name][member_path]

    def render(self, data: CollectorItem, options: GraphQLOptions) -> str:
        """Render the collected data.

        Args:
            data: The collected data.
            options: The options to use for rendering.

        Returns:
            The rendered data in HTML.
        """
        template_name = render.get_template(data)
        template = self.env.get_template(template_name)
        return template.render(
            **{
                "config": options,
                data.kind.value: data,
                "heading_level": options.heading_level,
                "root": True,
            }
        )

    def get_aliases(self, identifier: str) -> tuple[str, ...]:
        """Get aliases for a given identifier."""
        try:
            data = self._collected[identifier]
        except KeyError:
            return ()
        # Update the following code to return the canonical identifier and any aliases.
        return (data.path,)

    def update_env(self, config: dict[str, Any]) -> None:  # noqa: ARG002
        """Update the Jinja environment with any custom settings/filters/options
        for this handler.

        Args:
            config: MkDocs configuration, read from `mkdocs.yml`.
        """
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True
        self.env.keep_trailing_newline = False
        self.env.filters["format_signature"] = render.format_signature

    # You can also implement the `get_inventory_urls` and `load_inventory` methods
    # if you want to support loading object inventories.
    # You can also implement the `render_backlinks` method if you want to support backlinks.


def get_handler(
    handler_config: MutableMapping[str, Any],
    tool_config: MkDocsConfig,
    **kwargs: Any,
) -> GraphQLHandler:
    """Simply return an instance of `GraphQLHandler`.

    Arguments:
        handler_config: The handler configuration.
        tool_config: The tool (SSG) configuration.

    Returns:
        An instance of `GraphQLHandler`.
    """
    base_dir = Path(tool_config.config_file_path or "./mkdocs.yml").parent
    return GraphQLHandler(
        config=GraphQLConfig.from_data(**handler_config),
        base_dir=base_dir,
        **kwargs,
    )
