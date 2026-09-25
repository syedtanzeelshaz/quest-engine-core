"""
FastAPI GraphQL Router.

Mounts the Strawberry schema and wires context resolution for each request.
GraphiQL IDE is enabled in non-production environments or when explicitly enabled.
"""
from strawberry.fastapi import GraphQLRouter

from app.api.graphql.schema import schema
from app.core.config import settings
from app.graphql.common.constants import GRAPHIQL_IDE
from app.graphql.common.context import get_graphql_context

graphql_router = GraphQLRouter(
    schema=schema,
    context_getter=get_graphql_context,
    graphql_ide=GRAPHIQL_IDE if settings.is_graphql_ide_enabled else None,
)

