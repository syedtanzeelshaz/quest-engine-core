"""
Member data mutators (GraphQL mutation resolvers).
Uses GraphConstants and generated MemberUpdateInput contract without arbitrary resolve_ prefixes.
"""
from __future__ import annotations

from typing import Any

from ariadne import MutationType
from graphql import GraphQLResolveInfo
from questengine.registry import GraphConstants
from questengine.registry.types import Member as MemberGraphQL, MemberUpdateInput

from app.service.member.factory import build_member_service
from app.util.logger import log

member_mutation = MutationType()


@member_mutation.field(GraphConstants.MUTATION.MemberUpdate)
async def memberUpdate(
    _obj: Any,
    info: GraphQLResolveInfo,
    id: str,
    input: dict[str, Any],
) -> MemberGraphQL:
    """Update member personal profile details."""
    log.info("Received request to update member: %s", id)
    service = build_member_service()
    input_dto = MemberUpdateInput(**input)
    return await service.update_member(int(id), input_dto)
