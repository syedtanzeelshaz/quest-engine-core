"""
Member data loaders and field-level resolvers.
Maps SQLAlchemy model attributes (snake_case) to GraphQL schema fields (camelCase).
"""
from __future__ import annotations

from typing import Any

from ariadne import ObjectType
from graphql import GraphQLResolveInfo
from questengine.registry import GraphConstants

from app.model.identity.member import Member
from app.model.identity.role import Role

member_type = ObjectType(GraphConstants.MEMBER.TYPE_NAME)
role_type = ObjectType(GraphConstants.ROLE.TYPE_NAME)


@member_type.field(GraphConstants.MEMBER.Id)
def resolve_member_id(member: Member, _info: GraphQLResolveInfo) -> str:
    return str(member.id)


@member_type.field(GraphConstants.MEMBER.FirstName)
def resolve_member_first_name(member: Member, _info: GraphQLResolveInfo) -> str | None:
    return member.first_name


@member_type.field(GraphConstants.MEMBER.LastName)
def resolve_member_last_name(member: Member, _info: GraphQLResolveInfo) -> str | None:
    return member.last_name


@member_type.field(GraphConstants.MEMBER.DateOfBirth)
def resolve_member_dob(member: Member, _info: GraphQLResolveInfo) -> Any:
    return member.date_of_birth


@member_type.field(GraphConstants.MEMBER.JoinedAt)
def resolve_member_joined_at(member: Member, _info: GraphQLResolveInfo) -> Any:
    return member.joined_at


@member_type.field(GraphConstants.MEMBER.Roles)
def resolve_member_roles(member: Member, _info: GraphQLResolveInfo) -> list[Role]:
    return list(member.roles or [])


@role_type.field(GraphConstants.ROLE.Id)
def resolve_role_id(role: Role, _info: GraphQLResolveInfo) -> str:
    return str(role.id)


@role_type.field(GraphConstants.ROLE.Permissions)
def resolve_role_permissions(role: Role, _info: GraphQLResolveInfo) -> list[str]:
    # Returns role permissions or empty list if unpopulated
    return getattr(role, "permissions", [])
