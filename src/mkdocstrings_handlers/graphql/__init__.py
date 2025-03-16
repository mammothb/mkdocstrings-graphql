"""GraphQL handler for mkdocstrings."""

from mkdocstrings_handlers.graphql._internal.collections import SchemasCollection
from mkdocstrings_handlers.graphql._internal.config import (
    GraphQLConfig,
    GraphQLInputConfig,
    GraphQLInputOptions,
    GraphQLOptions,
)
from mkdocstrings_handlers.graphql._internal.docstring_models import (
    DocstringArgument,
    DocstringElement,
    DocstringNamedElement,
    DocstringReturn,
    DocstringSection,
    DocstringSectionArguments,
    DocstringSectionReturns,
)
from mkdocstrings_handlers.graphql._internal.enum import DocstringSectionKind, Kind
from mkdocstrings_handlers.graphql._internal.error import GraphQLFileSyntaxError
from mkdocstrings_handlers.graphql._internal.handler import GraphQLHandler, get_handler
from mkdocstrings_handlers.graphql._internal.loader import Loader
from mkdocstrings_handlers.graphql._internal.models import (
    Annotation,
    EnumTypeNode,
    Field,
    Input,
    InputObjectTypeNode,
    InterfaceTypeNode,
    Node,
    ObjectTypeNode,
    OperationTypeNode,
    ScalarTypeNode,
    Schema,
    SchemaDefinition,
    SchemaName,
    UnionTypeNode,
)
from mkdocstrings_handlers.graphql._internal.render import (
    format_signature,
    get_template,
)

__all__ = [
    "Annotation",
    "DocstringArgument",
    "DocstringElement",
    "DocstringNamedElement",
    "DocstringReturn",
    "DocstringSection",
    "DocstringSectionArguments",
    "DocstringSectionKind",
    "DocstringSectionReturns",
    "EnumTypeNode",
    "Field",
    "GraphQLConfig",
    "GraphQLFileSyntaxError",
    "GraphQLHandler",
    "GraphQLInputConfig",
    "GraphQLInputOptions",
    "GraphQLOptions",
    "Input",
    "InputObjectTypeNode",
    "InterfaceTypeNode",
    "Kind",
    "Loader",
    "Node",
    "ObjectTypeNode",
    "OperationTypeNode",
    "ScalarTypeNode",
    "Schema",
    "SchemaDefinition",
    "SchemaName",
    "SchemasCollection",
    "UnionTypeNode",
    "format_signature",
    "get_handler",
    "get_template",
]
