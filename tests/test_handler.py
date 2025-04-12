import pytest
from mkdocstrings import CollectionError

from mkdocstrings_handlers.graphql import GraphQLHandler, GraphQLOptions


@pytest.mark.parametrize("identifier", ["", "unsplittable"])
def test_collect_invalid_identifier(identifier: str, handler: GraphQLHandler) -> None:
    with pytest.raises(CollectionError, match=f"Failed to parse identifier '{identifier}'"):
        handler.collect(identifier, GraphQLOptions())


@pytest.mark.parametrize("identifier", ["schema.*", "schema.prefix.*"])
def test_collect_invalid_wildcard_directive(identifier: str, handler: GraphQLHandler) -> None:
    handler._schemas_collection["schema"] = {}
    with pytest.raises(CollectionError, match="Local configuration 'kind' must be set when using wildcard directive"):
        handler.collect(identifier, GraphQLOptions())


@pytest.mark.parametrize("identifier", ["schema.*", "schema.prefix.*"])
def test_collect_invalid_kind_value(identifier: str, handler: GraphQLHandler) -> None:
    handler._schemas_collection["schema"] = {}
    with pytest.raises(CollectionError, match="'kind' must be one of"):
        handler.collect(identifier, GraphQLOptions(kind="INVALID"))
