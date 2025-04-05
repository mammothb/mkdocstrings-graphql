from pathlib import Path

import pytest
from syrupy.assertion import SnapshotAssertion

from mkdocstrings_handlers.graphql._internal.error import GraphQLFileSyntaxError
from mkdocstrings_handlers.graphql._internal.loader import Loader
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
    UnionTypeNode,
)


def test_graphql_syntax_error(tmp_path: Path):
    schema_path = tmp_path / "schema.graphql"
    with open(schema_path, "w") as f:
        f.write("""
            type TestObject {
                field1: String!
                field2: String!
            """)

    with pytest.raises(GraphQLFileSyntaxError) as excinfo:
        Loader(schema_paths=[tmp_path])
    assert str(excinfo.value).startswith(f"Could not load {schema_path}")


def test_load_enum(tmp_path: Path):
    schema_path = tmp_path / "schema.graphql"
    with open(schema_path, "w") as f:
        f.write("""
            enum TestEnum {
                ENUM_VALUE_1
                ENUM_VALUE_2
            }
            """)

    loader = Loader(schema_paths=[tmp_path])
    loader.load(schema_name="schemaName")

    assert loader.schemas_collection["schemaName"]["TestEnum"] == EnumTypeNode(
        name="TestEnum",
        path="schemaName.TestEnum",
        description="",
        values=[EnumValue(name="ENUM_VALUE_1", description=""), EnumValue(name="ENUM_VALUE_2", description="")],
    )


def test_load_input(tmp_path: Path):
    with open(tmp_path / "schema.graphql", "w") as f:
        f.write("""
            input TestInput {
                field1: String!
                field2: String!
            }
            """)

    loader = Loader(schema_paths=[tmp_path])
    loader.load(schema_name="schemaName")

    assert loader.schemas_collection["schemaName"]["TestInput"] == InputObjectTypeNode(
        name="TestInput",
        path="schemaName.TestInput",
        description="",
        fields=[
            Input(
                name="field1",
                description="",
                type=Annotation(name="String", non_null=True, is_list=False, non_null_list=False),
            ),
            Input(
                name="field2",
                description="",
                type=Annotation(name="String", non_null=True, is_list=False, non_null_list=False),
            ),
        ],
    )


def test_load_interface(tmp_path: Path):
    with open(tmp_path / "schema.graphql", "w") as f:
        f.write("""
            interface TestInterface {
                field1: String!
                field2: String!
            }
            """)

    loader = Loader(schema_paths=[tmp_path])
    loader.load(schema_name="schemaName")

    assert loader.schemas_collection["schemaName"]["TestInterface"] == InterfaceTypeNode(
        name="TestInterface",
        path="schemaName.TestInterface",
        description="",
        fields=[
            Field(
                name="field1",
                description="",
                type=Annotation(name="String", non_null=True, is_list=False, non_null_list=False),
            ),
            Field(
                name="field2",
                description="",
                type=Annotation(name="String", non_null=True, is_list=False, non_null_list=False),
            ),
        ],
    )


def test_load_object(tmp_path: Path):
    with open(tmp_path / "schema.graphql", "w") as f:
        f.write("""
            type TestObject {
                field1: String!
                field2: String!
            }
            """)

    loader = Loader(schema_paths=[tmp_path])
    loader.load(schema_name="schemaName")

    assert loader.schemas_collection["schemaName"]["TestObject"] == ObjectTypeNode(
        name="TestObject",
        path="schemaName.TestObject",
        description="",
        fields=[
            Field(
                name="field1",
                description="",
                type=Annotation(name="String", non_null=True, is_list=False, non_null_list=False),
            ),
            Field(
                name="field2",
                description="",
                type=Annotation(name="String", non_null=True, is_list=False, non_null_list=False),
            ),
        ],
    )


def test_load_operation(tmp_path: Path):
    schema_path = tmp_path / "schema.graphql"
    with open(schema_path, "w") as f:
        f.write("""
            schema {
                mutation: Mutation
                query: Query
            }

            type Mutation {
                testMutation(
                    field1: String
                    field2: String
                ): Boolean
            }

            type Query {
                testQuery(
                    field1: String
                    field2: String
                ): Boolean
            }
            """)

    loader = Loader(schema_paths=[tmp_path])
    loader.load(schema_name="schemaName")

    assert loader.schemas_collection["schemaName"]["Mutation.testMutation"] == OperationTypeNode(
        name="testMutation",
        path="schemaName.Mutation.testMutation",
        description="",
        arguments=[
            Input(
                name="field1",
                description="",
                type=Annotation(name="String", non_null=False, is_list=False, non_null_list=False),
            ),
            Input(
                name="field2",
                description="",
                type=Annotation(name="String", non_null=False, is_list=False, non_null_list=False),
            ),
        ],
        type=Annotation(name="Boolean", non_null=False, is_list=False, non_null_list=False),
    )
    assert loader.schemas_collection["schemaName"]["Query.testQuery"] == OperationTypeNode(
        name="testQuery",
        path="schemaName.Query.testQuery",
        description="",
        arguments=[
            Input(
                name="field1",
                description="",
                type=Annotation(name="String", non_null=False, is_list=False, non_null_list=False),
            ),
            Input(
                name="field2",
                description="",
                type=Annotation(name="String", non_null=False, is_list=False, non_null_list=False),
            ),
        ],
        type=Annotation(name="Boolean", non_null=False, is_list=False, non_null_list=False),
    )


def test_load_scalar(tmp_path: Path):
    schema_path = tmp_path / "schema.graphql"
    with open(schema_path, "w") as f:
        f.write("scalar TestScalar")

    loader = Loader(schema_paths=[tmp_path])
    loader.load(schema_name="schemaName")

    assert loader.schemas_collection["schemaName"]["TestScalar"] == ScalarTypeNode(
        name="TestScalar", path="schemaName.TestScalar", description=""
    )


def test_load_schema_definition(tmp_path: Path):
    schema_path = tmp_path / "schema.graphql"
    with open(schema_path, "w") as f:
        f.write("""
            schema {
                mutation: Mutation
                query: Query
                subscription: Subscription
            }
            """)

    loader = Loader(schema_paths=[tmp_path])
    loader.load(schema_name="schemaName")

    assert loader.schemas_collection["schemaName"].definition is not None
    assert loader.schemas_collection["schemaName"].definition.mutation == "Mutation"
    assert loader.schemas_collection["schemaName"].definition.query == "Query"
    assert loader.schemas_collection["schemaName"].definition.subscription == "Subscription"
    assert loader.schemas_collection["schemaName"].definition.types == {"Mutation", "Query", "Subscription"}


def test_load_schema_definition_partial_definition(tmp_path: Path):
    schema_path = tmp_path / "schema.graphql"
    with open(schema_path, "w") as f:
        f.write("""
            schema {
                mutation: Mutation
                query: Query
            }
            """)

    loader = Loader(schema_paths=[tmp_path])
    loader.load(schema_name="schemaName")

    assert loader.schemas_collection["schemaName"].definition is not None
    assert loader.schemas_collection["schemaName"].definition.mutation == "Mutation"
    assert loader.schemas_collection["schemaName"].definition.query == "Query"
    assert loader.schemas_collection["schemaName"].definition.subscription is None
    assert loader.schemas_collection["schemaName"].definition.types == {"Mutation", "Query"}


def test_load_union(tmp_path: Path):
    schema_path = tmp_path / "schema.graphql"
    with open(schema_path, "w") as f:
        f.write("""
            type TestObject1 {
                field: String
            }

            type TestObject2 {
                field: String
            }

            union TestUnion = TestObject1 | TestObject2
            """)

    loader = Loader(schema_paths=[tmp_path])
    loader.load(schema_name="schemaName")

    assert "TestObject1" in loader.schemas_collection["schemaName"]
    assert "TestObject2" in loader.schemas_collection["schemaName"]
    assert loader.schemas_collection["schemaName"]["TestUnion"] == UnionTypeNode(
        name="TestUnion", path="schemaName.TestUnion", description="", types=["TestObject1", "TestObject2"]
    )


def test_parse_type(tmp_path: Path):
    with open(tmp_path / "schema.graphql", "w") as f:
        f.write("""
            type TestObject {
                nullElem: String
                nonNullElem: String!
                nullListNullElem: [String]
                nullListNonNullElem: [String!]
                nonNullListNullElem: [String]!
                nonNullListNonNullElem: [String!]!
            }
            """)

    loader = Loader(schema_paths=[tmp_path])
    loader.load(schema_name="schemaName")

    assert loader.schemas_collection["schemaName"]["TestObject"] == ObjectTypeNode(
        name="TestObject",
        path="schemaName.TestObject",
        description="",
        fields=[
            Field(
                name="nullElem",
                description="",
                type=Annotation(name="String", non_null=False, is_list=False, non_null_list=False),
            ),
            Field(
                name="nonNullElem",
                description="",
                type=Annotation(name="String", non_null=True, is_list=False, non_null_list=False),
            ),
            Field(
                name="nullListNullElem",
                description="",
                type=Annotation(name="String", non_null=False, is_list=True, non_null_list=False),
            ),
            Field(
                name="nullListNonNullElem",
                description="",
                type=Annotation(name="String", non_null=True, is_list=True, non_null_list=False),
            ),
            Field(
                name="nonNullListNullElem",
                description="",
                type=Annotation(name="String", non_null=False, is_list=True, non_null_list=True),
            ),
            Field(
                name="nonNullListNonNullElem",
                description="",
                type=Annotation(name="String", non_null=True, is_list=True, non_null_list=True),
            ),
        ],
    )


def test_load_multiple_files(snapshot: SnapshotAssertion):
    schema_dir = Path(__file__).parent / "fixtures" / "schema"

    loader = Loader(schema_paths=[schema_dir / "constructs.graphql", schema_dir / "schema.graphql"])
    loader.load(schema_name="schemaName")

    assert loader.schemas_collection["schemaName"] == snapshot
