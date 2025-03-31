"""Tests for our own API exposition."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

import griffe
import pytest
from mkdocstrings import Inventory

from mkdocstrings_handlers import graphql

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture(name="loader", scope="module")
def loader_fixture() -> griffe.GriffeLoader:
    loader = griffe.GriffeLoader()
    loader.load("mkdocstrings")
    loader.load("mkdocstrings_handlers.graphql")
    loader.resolve_aliases()
    return loader


@pytest.fixture(name="internal_api", scope="module")
def internal_api_fixture(loader: griffe.GriffeLoader) -> griffe.Module:
    return loader.modules_collection["mkdocstrings_handlers.graphql._internal"]


@pytest.fixture(name="public_api", scope="module")
def public_api_fixture(loader: griffe.GriffeLoader) -> griffe.Module:
    return loader.modules_collection["mkdocstrings_handlers.graphql"]


@pytest.fixture(name="modulelevel_internal_objects", scope="module")
def modulelevel_internal_objects_fixture(internal_api: griffe.Module) -> list[griffe.Object | griffe.Alias]:
    return list(_yield_public_objects(internal_api, modulelevel=True))


@pytest.fixture(name="internal_objects", scope="module")
def internal_objects_fixture(internal_api: griffe.Module) -> list[griffe.Object | griffe.Alias]:
    return list(_yield_public_objects(internal_api, modulelevel=False, special=True))


@pytest.fixture(name="public_objects", scope="module")
def public_objects_fixture(public_api: griffe.Module) -> list[griffe.Object | griffe.Alias]:
    return list(_yield_public_objects(public_api, modulelevel=False, inherited=True, special=True))


@pytest.fixture(name="inventory", scope="module")
def inventory_fixture() -> Inventory:
    inventory_file = Path(__file__).parent.parent / "site" / "objects.inv"
    if not inventory_file.exists():
        raise pytest.skip("The objects inventory is not available.")
    with inventory_file.open("rb") as file:
        return Inventory.parse_sphinx(file)


def _yield_public_objects(
    obj: griffe.Module | griffe.Class,
    *,
    modules: bool = False,
    modulelevel: bool = True,
    inherited: bool = False,
    special: bool = False,
) -> Iterator[griffe.Object | griffe.Alias]:
    for member in obj.all_members.values() if inherited else obj.members.values():
        try:
            if member.is_module:
                if member.is_alias or not member.is_public:
                    continue
                if modules:
                    yield member
                yield from _yield_public_objects(
                    member,  # pyright:ignore[reportArgumentType]
                    modules=modules,
                    modulelevel=modulelevel,
                    inherited=inherited,
                    special=special,
                )
            elif member.is_public and (special or not member.is_special):
                yield member
            else:
                continue
            if member.is_class and not modulelevel:
                yield from _yield_public_objects(
                    member,  # pyright:ignore[reportArgumentType]
                    modules=modules,
                    modulelevel=False,
                    inherited=inherited,
                    special=special,
                )
        except (griffe.AliasResolutionError, griffe.CyclicAliasError):
            continue


def test_unique_names(modulelevel_internal_objects: list[griffe.Object | griffe.Alias]) -> None:
    """All internal objects have unique names."""
    names_to_paths: dict[str, list[str]] = defaultdict(list)
    for obj in modulelevel_internal_objects:
        names_to_paths[obj.name].append(obj.path)
    non_unique = [paths for paths in names_to_paths.values() if len(paths) > 1]
    assert not non_unique, "Non-unique names:\n" + "\n".join(str(paths) for paths in non_unique)


def test_single_locations(public_api: griffe.Module) -> None:
    """All objects have a single public location."""

    def _public_path(obj: griffe.Object | griffe.Alias) -> bool:
        return obj.is_public and (obj.parent is None or _public_path(obj.parent))

    multiple_locations: dict[str, list[str]] = {}
    for obj_name in graphql.__all__:
        obj = public_api[obj_name]
        if obj.aliases and (
            public_aliases := [path for path, alias in obj.aliases.items() if path != obj.path and _public_path(alias)]
        ):
            multiple_locations[obj.path] = public_aliases
    assert not multiple_locations, "Multiple public locations:\n" + "\n".join(
        f"{path}: {aliases}" for path, aliases in multiple_locations.items()
    )


def test_no_module_docstrings_in_internal_api(internal_api: griffe.Module) -> None:
    """No module docstrings should be written in our internal API.

    The reasoning is that docstrings are addressed to users of the public API,
    but internal modules are not exposed to users, so they should not have docstrings.
    """

    def _modules(obj: griffe.Module) -> Iterator[griffe.Module]:
        for member in obj.modules.values():
            yield member
            yield from _modules(member)

    for obj in _modules(internal_api):
        assert not obj.docstring
