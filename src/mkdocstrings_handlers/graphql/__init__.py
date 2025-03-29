"""GraphQL handler for mkdocstrings."""

from mkdocstrings_handlers.graphql._internal.config import GraphQLOptions
from mkdocstrings_handlers.graphql._internal.handler import GraphQLHandler, get_handler

__all__ = ["GraphQLHandler", "GraphQLOptions", "get_handler"]
