from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from mkdocstrings import get_logger

from graphql.error.syntax_error import GraphQLSyntaxError
from graphql.language.ast import (
    EnumTypeDefinitionNode,
    EnumValueDefinitionNode,
    FieldDefinitionNode,
    InputObjectTypeDefinitionNode,
    InputValueDefinitionNode,
    InterfaceTypeDefinitionNode,
    ListTypeNode,
    NamedTypeNode,
    NonNullTypeNode,
    ObjectTypeDefinitionNode,
    ScalarTypeDefinitionNode,
    SchemaDefinitionNode,
    StringValueNode,
    TypeNode,
    UnionTypeDefinitionNode,
)
from graphql.language.parser import parse
from mkdocstrings_handlers.graphql._internal.collections import SchemasCollection
from mkdocstrings_handlers.graphql._internal.error import GraphQLFileSyntaxError
from mkdocstrings_handlers.graphql._internal.models import (
    Annotation,
    EnumTypeNode,
    EnumValue,
    Field,
    Input,
    InputObjectTypeNode,
    InterfaceTypeNode,
    ObjectTypeNode,
    OperationTypeNode,
    ScalarTypeNode,
    Schema,
    SchemaDefinition,
    SchemaName,
    UnionTypeNode,
)

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

    from graphql.language.ast import DocumentNode

_logger = get_logger(__name__)


class Loader:
    def __init__(
        self,
        *,
        schema_paths: Sequence[str | Path],
        schemas_collection: SchemasCollection | None = None,
    ) -> None:
        self.schemas_collection: SchemasCollection = schemas_collection or SchemasCollection()
        self.document: DocumentNode = self.load_schema(list(map(Path, schema_paths)))

    def load(self, schema_name: str) -> None:
        self._load_document(schema_name, self.document)

    def load_schema(self, paths: list[Path]) -> DocumentNode:
        if len(paths) > 1:
            partial_schemas = list(map(self._read_graph_file, sorted(paths)))
            schema = "\n".join(partial_schemas)
        elif (path := paths[0]).is_dir():
            partial_schemas = list(map(self._read_graph_file, sorted(self._walk_graphql_files(path))))
            schema = "\n".join(partial_schemas)
        else:
            schema = self._read_graph_file(path)

        return parse(schema)

    def _load_document(self, schema_name: SchemaName, doc_ast: DocumentNode) -> None:
        schema = Schema()
        for node in doc_ast.definitions:
            if type(node) is SchemaDefinitionNode:
                schema.definition = self._load_schema_definition(node)
                break
        for node in doc_ast.definitions:
            if type(node) is SchemaDefinitionNode:
                continue
            if type(node) is ScalarTypeDefinitionNode:
                schema[node.name.value] = self._load_scalar(schema_name, node)
            elif type(node) is InterfaceTypeDefinitionNode:
                schema[node.name.value] = self._load_interface(schema_name, node)
            elif type(node) is EnumTypeDefinitionNode:
                schema[node.name.value] = self._load_enum(schema_name, node)
            elif type(node) is UnionTypeDefinitionNode:
                schema[node.name.value] = self._load_union(schema_name, node)
            elif type(node) is ObjectTypeDefinitionNode:
                name = node.name.value
                if name in schema.operation_types:
                    for field_node in node.fields:
                        op_name = f"{name}.{field_node.name.value}"
                        schema.members[op_name] = self._load_operation(schema_name, name, field_node)
                else:
                    schema[name] = self._load_object(schema_name, node)
            elif type(node) is InputObjectTypeDefinitionNode:
                schema[node.name.value] = self._load_input(schema_name, node)
            else:
                _logger.warning(f"Unable to load {node} of type {type(node)}")
        self.schemas_collection[schema_name] = schema

    def _load_enum(self, schema_name: SchemaName, node: EnumTypeDefinitionNode) -> EnumTypeNode:
        name = node.name.value
        return EnumTypeNode(
            name=name,
            path=f"{schema_name}.{name}",
            description=self._parse_description(node.description),
            values=self._parse_enum_values(node.values),
        )

    def _load_input(self, schema_name: SchemaName, node: InputObjectTypeDefinitionNode) -> InputObjectTypeNode:
        name = node.name.value
        return InputObjectTypeNode(
            name=name,
            path=f"{schema_name}.{name}",
            description=self._parse_description(node.description),
            fields=self._parse_input_values(node.fields),
        )

    def _load_interface(self, schema_name: SchemaName, node: InterfaceTypeDefinitionNode) -> InterfaceTypeNode:
        name = node.name.value
        return InterfaceTypeNode(
            name=name,
            path=f"{schema_name}.{name}",
            description=self._parse_description(node.description),
            fields=self._parse_fields(node.fields),
        )

    def _load_object(self, schema_name: SchemaName, node: ObjectTypeDefinitionNode) -> ObjectTypeNode:
        name = node.name.value
        return ObjectTypeNode(
            name=name,
            path=f"{schema_name}.{name}",
            description=self._parse_description(node.description),
            fields=self._parse_fields(node.fields),
        )

    def _load_operation(self, schema: str, op_name: str, node: FieldDefinitionNode) -> OperationTypeNode:
        name = node.name.value
        return OperationTypeNode(
            name=name,
            path=f"{schema}.{op_name}.{name}",
            description=self._parse_description(node.description),
            arguments=self._parse_input_values(node.arguments),
            type=self._parse_type(node.type),
        )

    def _load_scalar(self, schema_name: SchemaName, node: ScalarTypeDefinitionNode) -> ScalarTypeNode:
        name = node.name.value
        return ScalarTypeNode(
            name=name,
            path=f"{schema_name}.{name}",
            description=self._parse_description(node.description),
        )

    def _load_schema_definition(self, node: SchemaDefinitionNode) -> SchemaDefinition:
        return SchemaDefinition(
            **{op_type.operation.value: op_type.type.name.value for op_type in node.operation_types}
        )

    def _load_union(self, schema_name: SchemaName, node: UnionTypeDefinitionNode) -> UnionTypeNode:
        name = node.name.value
        return UnionTypeNode(
            name=name,
            path=f"{schema_name}.{name}",
            description=self._parse_description(node.description),
            types=[type_node.name.value for type_node in node.types],
        )

    def _parse_enum_values(self, nodes: tuple[EnumValueDefinitionNode, ...]) -> list[EnumValue]:
        return [
            EnumValue(
                name=node.name.value,
                description=self._parse_description(node.description),
            )
            for node in nodes
        ]

    def _parse_fields(self, nodes: tuple[FieldDefinitionNode, ...]) -> list[Field]:
        return [
            Field(
                name=node.name.value,
                description=self._parse_description(node.description),
                type=self._parse_type(node.type),
            )
            for node in nodes
        ]

    def _parse_description(self, node: StringValueNode | None) -> str:
        return node.value if node is not None else ""

    def _parse_input_values(self, nodes: tuple[InputValueDefinitionNode, ...]) -> list[Input]:
        return [
            Input(
                name=node.name.value,
                description=self._parse_description(node.description),
                type=self._parse_type(node.type),
            )
            for node in nodes
        ]

    def _parse_type(
        self,
        node: TypeNode,
        *,
        non_null: bool = False,
        is_list: bool = False,
        non_null_list: bool = False,
    ) -> Annotation:
        """Recursively parses types.

        The following combinations are possible:
        BaseType, BaseType!, [BaseType], [BaseType!], [BaseType]!, [BaseType!]!
        """
        if type(node) is NonNullTypeNode:
            if type(node.type) is ListTypeNode:
                return self._parse_type(
                    node.type,
                    non_null=non_null,
                    is_list=is_list,
                    non_null_list=True,
                )
            return self._parse_type(
                node.type,
                non_null=True,
                is_list=is_list,
                non_null_list=non_null_list,
            )

        if type(node) is ListTypeNode:
            return self._parse_type(
                node.type,
                non_null=non_null,
                is_list=True,
                non_null_list=non_null_list,
            )
        if type(node) is NamedTypeNode:
            return Annotation(
                name=node.name.value,
                non_null=non_null,
                is_list=is_list,
                non_null_list=non_null_list,
            )
        msg = f"Unknown type {node.to_dict()}"
        raise ValueError(msg)

    def _read_graph_file(self, path: Path) -> str:
        with open(path, encoding="utf-8") as f:
            schema = f.read()
        try:
            _ = parse(schema)
        except GraphQLSyntaxError as e:
            raise GraphQLFileSyntaxError(path, str(e)) from e
        return schema

    def _walk_graphql_files(self, path: Path) -> Generator[Path]:
        extensions = (".graphql", ".graphqls", "gql")
        for dirpath, _, filenames in os.walk(str(path)):
            for name in filenames:
                if name.lower().endswith(extensions):
                    yield Path(dirpath) / name
