import pytest
from mkdocstrings import CollectionError

from mkdocstrings_handlers.graphql import GraphQLHandler, GraphQLOptions


@pytest.mark.parametrize("identifier", ["", "unsplittable"])
def test_collect_invalid_identifier(identifier: str, handler: GraphQLHandler) -> None:
    with pytest.raises(CollectionError, match=f"Failed to parse identifier '{identifier}'"):
        handler.collect(identifier, GraphQLOptions())
