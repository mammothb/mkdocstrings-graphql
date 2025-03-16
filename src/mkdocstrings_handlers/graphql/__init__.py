"""Graphql handler for mkdocstrings."""

from mkdocstrings_handlers.graphql._internal.config import (
    GraphqlConfig,
    GraphqlInputConfig,
    GraphqlInputOptions,
    GraphqlOptions,
)
from mkdocstrings_handlers.graphql._internal.handler import GraphqlHandler, get_handler

__all__ = [
    "GraphqlConfig",
    "GraphqlHandler",
    "GraphqlInputConfig",
    "GraphqlInputOptions",
    "GraphqlOptions",
    "get_handler",
]
