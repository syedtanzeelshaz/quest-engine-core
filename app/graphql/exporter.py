"""
Schema Exporter Script.

Compiles the current Strawberry GraphQL schema and exports it as an SDL (.graphql) file.
Executed directly via:
    python -m app.graphql.exporter [output_path]
"""
from collections.abc import Iterable
from itertools import chain
from pathlib import Path
import sys
from typing import Any, cast

from graphql import (
    GraphQLEnumType,
    GraphQLInputObjectType,
    GraphQLInterfaceType,
    GraphQLNamedType,
    GraphQLObjectType,
    GraphQLScalarType,
    GraphQLSchema,
    GraphQLUnionType,
)
from strawberry import Schema
from strawberry.printer.printer import (
    PrintExtras,
    _get_schema_type_names,
    _print_type,
    _should_print_type,
    is_builtin_directive,
    is_defined_type,
    print_directive,
    print_schema_definition,
)
from strawberry.types.scalar import ScalarWrapper

from app.api.graphql.schema import schema
from app.graphql.common.constants import DEFAULT_SCHEMA_OUTPUT_PATH
from app.util.logger import log


def _graphql_type_sort_key(type_: GraphQLNamedType) -> tuple[int, str]:
    name = type_.name

    # 1. Root Query
    if isinstance(type_, GraphQLObjectType) and name == "Query":
        return (0, name)

    # 2. Root Mutation
    if isinstance(type_, GraphQLObjectType) and name == "Mutation":
        return (1, name)

    # 3. Root Subscription
    if isinstance(type_, GraphQLObjectType) and name == "Subscription":
        return (2, name)

    # 4. Input types (CreateOrganizationInput, UpdateUserProfileInput, etc.)
    if isinstance(type_, GraphQLInputObjectType):
        return (3, name)

    # 5. Object types (Organization, User, etc.)
    if isinstance(type_, GraphQLObjectType):
        return (4, name)

    # 6. Interfaces and Unions
    if isinstance(type_, (GraphQLInterfaceType, GraphQLUnionType)):
        return (5, name)

    # 7. Custom Scalars (Date, DateTime, etc.)
    if isinstance(type_, GraphQLScalarType):
        return (6, name)

    # 8. Enums (AppUserStatus, CountryCode, etc.)
    if isinstance(type_, GraphQLEnumType):
        return (7, name)

    return (8, name)


def print_schema_ordered(schema_instance: Schema) -> str:
    """
    Print the Strawberry schema preserving native formatting while logically ordering types:
    Query -> Mutation -> Inputs -> Types -> Interfaces/Unions -> Scalars -> Enums.
    """
    graphql_core_schema = cast("GraphQLSchema", schema_instance._schema)
    extras = PrintExtras()

    filtered_directives = [
        directive
        for directive in graphql_core_schema.directives
        if not is_builtin_directive(directive)
    ]

    type_map = graphql_core_schema.type_map
    schema_type_names = _get_schema_type_names(schema_instance)

    # Filter defined, printable types
    printable_types = [
        t
        for t_name in type_map
        if is_defined_type(t := type_map[t_name])
        and _should_print_type(t, schema_type_names)
    ]

    sorted_types = sorted(printable_types, key=_graphql_type_sort_key)
    types_printed = [_print_type(t, schema_instance, extras=extras) for t in sorted_types]
    schema_definition = print_schema_definition(schema_instance, extras=extras)

    def _name_getter(t: Any) -> str:
        if hasattr(t, "name"):
            return t.name
        if isinstance(t, ScalarWrapper):
            return t._scalar_definition.name
        return t.__name__

    def _print_extra_types() -> Iterable[str]:
        for t in sorted(extras.types, key=_name_getter):
            graphql_type = cast(
                "GraphQLNamedType", schema_instance.schema_converter.from_type(t)
            )
            if not _should_print_type(graphql_type, schema_type_names):
                continue
            if graphql_type.name in type_map:
                continue
            yield _print_type(graphql_type, schema_instance, extras=extras)

    extra_types_printed = list(_print_extra_types())
    directives = [
        printed_directive
        for directive in filtered_directives
        if (printed_directive := print_directive(directive, schema=schema_instance)) is not None
        and printed_directive not in extras.directives
    ]

    sdl = "\n\n".join(
        chain(
            sorted(extras.directives),
            filter(None, [schema_definition]),
            directives,
            types_printed,
            extra_types_printed,
        )
    )
    return f"{sdl.strip()}\n"


def export_schema(output_path: str = DEFAULT_SCHEMA_OUTPUT_PATH) -> None:
    """Export the compiled Strawberry schema as formatted and organized raw SDL."""
    sdl = print_schema_ordered(schema)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(sdl)
    log.info("[export_schema] Schema successfully exported to %s — %d lines", output_path, len(sdl.splitlines()))


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SCHEMA_OUTPUT_PATH
    export_schema(target)


# Direct execution entrypoint (e.g. `python -m app.graphql.exporter [output_path]`)
if __name__ == "__main__":
    main()

