"""
Member data mutators (GraphQL mutation resolvers).
Uses GraphConstants and generated MemberUpdateInput contract.
"""
from __future__ import annotations

from typing import Any

from ariadne import MutationType
from graphql import GraphQLResolveInfo
from questengine.registry import GraphConstants
from questengine.registry.types import MemberUpdateInput

from app.model.identity.member import Member
from app.service.member.factory import build_member_service

member_mutation = MutationType()


@member_mutation.field(GraphConstants.MUTATION.MemberUpdate)
async def resolve_member_update(
    _obj: Any,
    info: GraphQLResolveInfo,
    id: str,
    input: dict[str, Any],
) -> Member:
    """Resolve memberUpdate mutation using authoritative MemberUpdateInput contract."""
    service = build_member_service()
    input_dto = MemberUpdateInput(**input)
    return await service.update_member(int(id), input_dto)
