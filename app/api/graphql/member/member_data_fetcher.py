"""
Member data fetchers.
Provides query and child field resolvers for Member domain operations.
"""
from __future__ import annotations

from typing import Any

from ariadne import ObjectType, QueryType
from graphql import GraphQLResolveInfo
from questengine.registry import GraphConstants
from questengine.registry.types import Member as MemberGraphQL, Role as RoleGraphQL

from app.api.graphql.member.member_data_loader import MemberDataLoader
from app.graphql.context import GraphQLContext
from app.service.member.factory import build_member_service
from app.util.logger import log

member_query = QueryType()
member_type = ObjectType(GraphConstants.MEMBER.TYPE_NAME)


@member_query.field(GraphConstants.QUERY.Member)
async def member(
    _obj: Any,
    info: GraphQLResolveInfo,
    id: str,
) -> MemberGraphQL | None:
    """Retrieve member by ID for customer or operations experience."""
    log.info("Received request to fetch member: %s", id)
    service = build_member_service()
    return await service.get_member(int(id))


@member_type.field(GraphConstants.MEMBER.Roles)
async def roles(
    parent: MemberGraphQL,
    info: GraphQLResolveInfo,
) -> list[RoleGraphQL]:
    """
    Child field resolver for Member.roles.
    Delegates to MemberDataLoader to batch role fetching across members and eliminate N+1 queries.
    """
    context: GraphQLContext = info.context
    loader = context.get_loader("member_data_loader", MemberDataLoader)
    return await loader.load_roles(int(parent.id))
