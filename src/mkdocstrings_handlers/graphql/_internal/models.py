from __future__ import annotations

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
from mkdocstrings_handlers.graphql._internal.enum import Kind

if TYPE_CHECKING:
    from collections.abc import Sequence

SchemaName = str


@dataclass
class Node:
    """An abstract class representing a GraphQL node."""

    kind: ClassVar[Kind]

    name: str
    path: str


@dataclass
class Annotation:
    name: str
    non_null: bool
    is_list: bool
    non_null_list: bool

    @property
    def render(self) -> str:
        rendered = self.name
        if self.non_null:
            rendered = f"{rendered}!"
        if self.is_list:
            rendered = f"[{rendered}]"
        if self.non_null_list:
            rendered = f"{rendered}!"
        return rendered


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
    types: set[str] = field(init=False)

    def __post_init__(self) -> None:
        self.types = {
            type_name
            for type_name in (self.mutation, self.query, self.subscription)
            if type_name is not None
        }


@dataclass
class Schema:
    kind: Kind = Kind.SCHEMA

    definition: SchemaDefinition | None = None
    members: dict[str, Node] = field(default_factory=dict)

    def __getitem__(self, key: Any) -> Node:
        return self.members[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        self.members[key] = value

    @property
    def operation_types(self) -> set[str]:
        return getattr(self.definition, "types", set())


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
                value=[
                    DocstringEnumValue(name=value.name, description=value.description)
                    for value in self.values
                ]
            ),
        ]


@dataclass
class InterfaceTypeNode(Node):
    kind: ClassVar[Kind] = Kind.INTERFACE

    description: str
    fields: list[Field]


@dataclass
class InputObjectTypeNode(Node):
    kind: ClassVar[Kind] = Kind.OBJECT

    description: str
    fields: list[Input]

    @property
    def docstring(self) -> Sequence[DocstringSection]:
        return [
            DocstringSectionText(value=self.description),
            DocstringSectionFields(
                value=[
                    DocstringField(
                        name=field.name,
                        description=field.description,
                        annotation=field.type.render,
                    )
                    for field in self.fields
                ]
            ),
        ]


@dataclass
class ObjectTypeNode(Node):
    kind: ClassVar[Kind] = Kind.OBJECT

    description: str
    fields: list[Field]

    @property
    def docstring(self) -> Sequence[DocstringSection]:
        return [
            DocstringSectionText(value=self.description),
            DocstringSectionFields(
                value=[
                    DocstringField(
                        name=field.name,
                        description=field.description,
                        annotation=field.type.render,
                    )
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
                    DocstringArgument(
                        name=argument.name,
                        description=argument.description,
                        annotation=argument.type.render,
                    )
                    for argument in self.arguments
                ]
            ),
            DocstringSectionReturns(
                value=[DocstringReturn(description="", annotation=self.type.render)]
            ),
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
    types: list[str]

    @property
    def docstring(self) -> Sequence[DocstringSection]:
        return [DocstringSectionText(value=self.description)]
