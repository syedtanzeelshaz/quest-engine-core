"""
GraphQL presentation router.
Wires the authoritative schema, domain resolvers, context builder, and mounts the Ariadne ASGI app.
"""
from __future__ import annotations

from ariadne.asgi import GraphQL

from app.api.graphql.context_builder import build_graphql_context
from app.api.graphql.member import MEMBER_RESOLVERS
from app.graphql.schema import build_schema

# Compile authoritative schema with all registered domain resolvers
executable_schema = build_schema(*MEMBER_RESOLVERS)

# Initialize Ariadne ASGI GraphQL handler with per-request context builder
graphql_app = GraphQL(
    schema=executable_schema,
    context_value=build_graphql_context,
)

__all__ = [
    "executable_schema",
    "graphql_app",
]
