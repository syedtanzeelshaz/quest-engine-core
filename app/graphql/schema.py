"""
Authoritative schema compiler.
Loads supergraph SDL from questengine.registry, binds custom scalars, directives, and domain resolvers.
"""
from __future__ import annotations

from typing import Sequence

from ariadne import SchemaBindable, make_executable_schema
from graphql import GraphQLSchema
from questengine.registry import get_supergraph_path

from app.graphql.directives.authorize import AuthorizeDirective
from app.graphql.scalars import ALL_SCALARS


def build_schema(*resolvers: SchemaBindable) -> GraphQLSchema:
    """
    Compile the executable GraphQL schema combining authoritative supergraph SDL,
    built-in scalars, directives, and domain-level resolvers.
    """
    supergraph_path = get_supergraph_path()
    sdl = supergraph_path.read_text(encoding="utf-8")

    all_bindables: list[SchemaBindable] = [*ALL_SCALARS, *resolvers]

    return make_executable_schema(
        sdl,
        all_bindables,
        directives={"authorize": AuthorizeDirective},
    )
