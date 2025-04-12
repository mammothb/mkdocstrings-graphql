from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from mkdocstrings_handlers.graphql._internal.docstring_models import (
    DocstringArgument,
    DocstringEnumValue,
    DocstringField,
    DocstringReturn,
    DocstringSection,
    DocstringSectionArguments,
    DocstringSectionEnumValues,
    DocstringSectionFields,
    DocstringSectionReturns,
    DocstringSectionText,
)
from mkdocstrings_handlers.graphql._internal.enumerations import Kind

if TYPE_CHECKING:
    from collections.abc import Generator, ItemsView, KeysView, Sequence, ValuesView

    from mkdocstrings_handlers.graphql._internal.expressions import Annotation, TypeName

SchemaName = str


@dataclass
class Node:
    """An abstract class representing a GraphQL node."""

    kind: ClassVar[Kind]

    name: str
    path: str


@dataclass
class EnumValue:
    name: str
    description: str


@dataclass
class Field:
    name: str
    description: str
    type: Annotation


@dataclass
class Input:
    name: str
    description: str
    type: Annotation


@dataclass
class SchemaDefinition:
    mutation: str | None = None
    query: str | None = None
    subscription: str | None = None
    types: frozenset[str] = field(init=False)

    def __post_init__(self) -> None:
        self.types = frozenset(
            type_name for type_name in (self.mutation, self.query, self.subscription) if type_name is not None
        )


@dataclass
class Schema:
    kind: Kind = Kind.SCHEMA

    definition: SchemaDefinition | None = None
    members: dict[str, Node] = field(default_factory=dict)

    def __contains__(self, item: Any) -> bool:
        return item in self.members

    def __getitem__(self, key: Any) -> Node:
        return self.members[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        self.members[key] = value

    @property
    def operation_types(self) -> frozenset[str]:
        return getattr(self.definition, "types", frozenset())

    def glob(self, pattern: str) -> Generator[Node]:
        for key, value in self.items():
            if fnmatch.fnmatch(key, pattern):
                yield value

    def items(self) -> ItemsView[str, Node]:
        return self.members.items()

    def keys(self) -> KeysView[str]:
        return self.members.keys()

    def values(self) -> ValuesView[Node]:
        return self.members.values()


#######
# Nodes
#######
@dataclass
class EnumTypeNode(Node):
    kind: ClassVar[Kind] = Kind.ENUM

    description: str
    values: list[EnumValue]

    @property
    def docstring(self) -> Sequence[DocstringSection]:
        return [
            DocstringSectionText(value=self.description),
            DocstringSectionEnumValues(
                value=[DocstringEnumValue(name=value.name, description=value.description) for value in self.values]
            ),
        ]


@dataclass
class InterfaceTypeNode(Node):
    kind: ClassVar[Kind] = Kind.INTERFACE

    description: str
    fields: list[Field]
    interfaces: list[TypeName]

    @property
    def docstring(self) -> Sequence[DocstringSection]:
        return [
            DocstringSectionText(value=self.description),
            DocstringSectionFields(
                value=[
                    DocstringField(name=field.name, description=field.description, annotation=field.type)
                    for field in self.fields
                ]
            ),
        ]


@dataclass
class InputObjectTypeNode(Node):
    kind: ClassVar[Kind] = Kind.INPUT

    description: str
    fields: list[Input]

    @property
    def docstring(self) -> Sequence[DocstringSection]:
        return [
            DocstringSectionText(value=self.description),
            DocstringSectionFields(
                value=[
                    DocstringField(name=field.name, description=field.description, annotation=field.type)
                    for field in self.fields
                ]
            ),
        ]


@dataclass
class ObjectTypeNode(Node):
    kind: ClassVar[Kind] = Kind.OBJECT

    description: str
    fields: list[Field]
    interfaces: list[TypeName]

    @property
    def docstring(self) -> Sequence[DocstringSection]:
        return [
            DocstringSectionText(value=self.description),
            DocstringSectionFields(
                value=[
                    DocstringField(name=field.name, description=field.description, annotation=field.type)
                    for field in self.fields
                ]
            ),
        ]


@dataclass
class OperationTypeNode(Node):
    kind: ClassVar[Kind] = Kind.OPERATION

    description: str
    arguments: list[Input]
    type: Annotation

    @property
    def docstring(self) -> Sequence[DocstringSection]:
        return [
            DocstringSectionText(value=self.description),
            DocstringSectionArguments(
                value=[
                    DocstringArgument(name=argument.name, description=argument.description, annotation=argument.type)
                    for argument in self.arguments
                ]
            ),
            DocstringSectionReturns(value=[DocstringReturn(description="", annotation=self.type)]),
        ]


@dataclass
class ScalarTypeNode(Node):
    kind: ClassVar[Kind] = Kind.SCALAR

    description: str

    @property
    def docstring(self) -> Sequence[DocstringSection]:
        return [DocstringSectionText(value=self.description)]


@dataclass
class UnionTypeNode(Node):
    kind: ClassVar[Kind] = Kind.UNION

    description: str
    types: list[TypeName]

    @property
    def docstring(self) -> Sequence[DocstringSection]:
        return [DocstringSectionText(value=self.description)]
