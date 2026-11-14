"""
Member data fetchers (GraphQL query resolvers).
Uses GraphConstants for type-safe resolver bindings.
"""
from __future__ import annotations

from typing import Any

from ariadne import QueryType
from graphql import GraphQLResolveInfo
from questengine.registry import GraphConstants

from app.graphql.context import GraphQLContext
from app.model.identity.member import Member
from app.service.member.factory import build_member_service

member_query = QueryType()


@member_query.field(GraphConstants.QUERY.Member)
async def resolve_member(
    _obj: Any,
    info: GraphQLResolveInfo,
    id: str,
) -> Member | None:
    """Resolve member by ID for customer or operations experience."""
    service = build_member_service()
    return await service.get_member(int(id))
