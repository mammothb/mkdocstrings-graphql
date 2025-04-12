from __future__ import annotations

import glob
import sys
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, final

from mkdocs.exceptions import PluginError
from mkdocstrings import BaseHandler, CollectionError, CollectorItem, get_logger

from mkdocstrings_handlers.graphql._internal import render
from mkdocstrings_handlers.graphql._internal.collections import SchemasCollection
from mkdocstrings_handlers.graphql._internal.config import GraphQLConfig, GraphQLOptions
from mkdocstrings_handlers.graphql._internal.enum import Kind
from mkdocstrings_handlers.graphql._internal.loader import Loader

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping, MutableMapping

    from mkdocs.config.defaults import MkDocsConfig
    from mkdocstrings import HandlerOptions

    from mkdocstrings_handlers.graphql._internal.models import SchemaName

if sys.version_info >= (3, 11):
    from contextlib import chdir
else:
    import os  # pyright:ignore[reportUnreachable]
    from contextlib import contextmanager
    from pathlib import Path

    @contextmanager
    def chdir(path: Path) -> Iterator[None]:
        curr_dir = os.getcwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(curr_dir)


if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override  # pyright:ignore[reportUnreachable]


_logger = get_logger(__name__)


@final
class GraphQLHandler(BaseHandler):
    """The GraphQL handler class.

    Attributes:
        name: The handler's name.
        domain: The cross-documentation domain/language for this handler.
        enable_inventory: Whether this handler is interested in enabling the
            creation of the 'objects.inv' Sphinx inventory file.
        fallback_theme: The theme to fallback to.
        config: The handler configuration.
        base_dir: The base directory of the project.
        global_options: The handler configuration options.
    """

    name: ClassVar[str] = "graphql"
    domain: ClassVar[str] = "graphql"
    enable_inventory: ClassVar[bool] = False
    fallback_theme: ClassVar[str] = "material"

    def __init__(self, config: GraphQLConfig, base_dir: Path, **kwargs: Any) -> None:
        """Initializes the handler.

        Args:
            config: The handler configuration.
            base_dir: The base directory of the project.
            **kwargs: Arguments passed to the parent constructor.
        """
        super().__init__(**kwargs)

        self.config = config
        self.base_dir = base_dir
        self.global_options = config.handler_options

        schemas = config.schemas or {}
        with chdir(self.base_dir):
            resolved_schemas: dict[SchemaName, list[str]] = {}
            for name, paths in schemas.items():
                resolved_schemas[name] = []
                for path in paths:
                    resolved_schemas[name].extend(glob.glob(path))

        self._schema_to_paths: dict[SchemaName, list[str]] = resolved_schemas
        self._schemas_collection: SchemasCollection = SchemasCollection()

        self._collected: dict[str, CollectorItem] = {}

    @override
    def get_options(self, local_options: Mapping[str, Any]) -> HandlerOptions:
        """Combines default, global, and local options.

        Args:
            local_options: The local options.

        Returns:
            The combined options.
        """
        options = {**asdict(self.global_options), **local_options}
        try:
            return GraphQLOptions.from_data(**options)
        except Exception as error:
            msg = f"Invalid options: {error}"
            raise PluginError(msg) from error

    @override
    def collect(self, identifier: str, options: GraphQLOptions) -> CollectorItem | list[CollectorItem]:
        """Collects data given an identifier and selection configuration.

        Args:
            identifier: The identifier of the object to collect.
            options: The options to use for the collection.

        Returns:
            The collected item or a list of collected items if a wildcard
            directive is provided.

        Raises:
            CollectionError: If ``identifier`` cannot be parsed into two parts.
            CollectionError: If a wildcard directive is provided by local option
                'kind' is not specified.
            CollectionError: If local option 'kind' is invalid.
        """
        try:
            schema_name, member_path = identifier.split(".", 1)
        except Exception as err:
            msg = f"Failed to parse identifier '{identifier}'"
            raise CollectionError(msg) from err

        is_wildcard_directive = member_path == "*"

        if is_wildcard_directive and options.kind is None:
            msg = "Local configuration 'kind' must be set when using wildcard directive"
            raise CollectionError(msg)

        if not is_wildcard_directive and options.kind is not None:
            _logger.warning("Local option 'kind' has no effect when not using wildcard directive")

        unknown_schema = schema_name not in self._schemas_collection
        if unknown_schema:
            loader = Loader(
                schema_paths=self._schema_to_paths[schema_name],
                schemas_collection=self._schemas_collection,
            )
            loader.load(schema_name)

        if is_wildcard_directive:
            try:
                assert options.kind is not None
                kind = Kind[options.kind]
            except Exception as err:
                msg = f"'kind' must be one of {Kind.public_members()}"
                raise CollectionError(msg) from err

            items = [item for item in self._schemas_collection[schema_name].values() if item.kind == kind]
            return items

        return self._schemas_collection[schema_name][member_path]

    @override
    def render(self, data: CollectorItem | list[CollectorItem], options: GraphQLOptions) -> str:
        """Renders the collected data.

        Args:
            data: The collected data.
            options: The options to use for rendering.

        Returns:
            The rendered data in HTML.
        """
        if isinstance(data, list):
            rendered = []
            for item in data:
                rendered.append(self.render(item, options))
            return "".join(rendered)

        template_name = render.get_template(data)
        template = self.env.get_template(template_name)
        return template.render(
            **{
                "config": options,
                render.map_kind(data.kind): data,
                "heading_level": options.heading_level,
                "root": True,
            }
        )

    @override
    def get_aliases(self, identifier: str) -> tuple[str, ...]:
        """Get aliases for a given identifier."""
        try:
            data = self._collected[identifier]
        except KeyError:
            return ()
        # Update the following code to return the canonical identifier and any aliases.
        return (data.path,)

    @override
    def update_env(self, config: dict[str, Any]) -> None:
        """Updates the Jinja environment with any custom
        settings/filters/options for this handler.

        Args:
            config: MkDocs configuration, read from `mkdocs.yml`.
        """
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True
        self.env.keep_trailing_newline = False
        self.env.filters["format_signature"] = render.format_signature  # pyright:ignore[reportArgumentType]


def get_handler(handler_config: MutableMapping[str, Any], tool_config: MkDocsConfig, **kwargs: Any) -> GraphQLHandler:
    """Returns an instance of `GraphQLHandler`.

    Args:
        handler_config: The handler configuration.
        tool_config: The tool (SSG) configuration.

    Returns:
        An instance of `GraphQLHandler`.
    """
    base_dir = Path(tool_config.config_file_path or "./mkdocs.yml").parent
    return GraphQLHandler(config=GraphQLConfig.from_data(**handler_config), base_dir=base_dir, **kwargs)
