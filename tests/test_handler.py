import pytest
from mkdocstrings import CollectionError

from mkdocstrings_handlers.graphql import GraphQLHandler, GraphQLOptions


def test_collect_empty_identifier(handler: GraphQLHandler) -> None:
    with pytest.raises(CollectionError, match="Empty identifier"):
        handler.collect("", GraphQLOptions())
