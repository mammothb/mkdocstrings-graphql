from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Expr:
    canonical_path: str | None = field(init=False)

    def __post_init__(self) -> None:
        self.canonical_path = None

    @property
    def class_name(self) -> str:
        return self.__class__.__name__


@dataclass
class TypeName(Expr):
    name: str

    @property
    def render(self) -> str:
        return self.name


@dataclass
class Annotation(Expr):
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
