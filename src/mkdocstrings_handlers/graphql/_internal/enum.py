import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class DocstringSectionKind(StrEnum):
    ARGUMENTS = "arguments"
    RETURNS = "returns"


class Kind(StrEnum):
    ENUM = "enum"
    INPUT = "input"
    INTERFACE = "interface"
    OBJECT = "object"
    OPERATION = "operation"
    SCALAR = "scalar"
    SCHEMA = "schema"
    TYPE = "type"
    UNION = "union"
