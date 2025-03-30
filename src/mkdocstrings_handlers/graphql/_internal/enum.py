import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class DocstringSectionKind(StrEnum):
    ARGUMENTS = "arguments"
    ENUM_VALUES = "enum_values"
    FIELDS = "fields"
    RETURNS = "returns"


class Kind(StrEnum):
    ENUM = "gql_enum"
    INPUT = "gql_input"
    INTERFACE = "gql_interface"
    OBJECT = "gql_object"
    OPERATION = "gql_operation"
    SCALAR = "gql_scalar"
    SCHEMA = "gql_schema"
    TYPE = "gql_type"
    UNION = "gql_union"
