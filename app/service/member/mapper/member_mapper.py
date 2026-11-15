"""
Member domain mappers.
Transforms identity.member domain models into authoritative GraphQL response dataclasses.
"""
from __future__ import annotations

from questengine.registry.types import Member as MemberGraphQL

from app.model.identity.member import Member


class MemberMapper:
    """Transforms identity.member domain models into GraphQL schema dataclasses."""

    @staticmethod
    def to_graphql(source: Member | None) -> MemberGraphQL | None:
        """Map a Member ORM entity to the generated GraphQL Member dataclass."""
        if source is None:
            return None

        return MemberGraphQL(
            id=str(source.id),
            email=source.email,
            firstName=source.first_name,
            lastName=source.last_name,
            phone=source.phone,
            country=source.country,
            gender=source.gender,
            dateOfBirth=source.date_of_birth,
            status=source.status,
            joinedAt=source.joined_at,
        )


    @classmethod
    def to_graphql_list(cls, sources: list[Member]) -> list[MemberGraphQL]:
        """Map a list of Member ORM entities to GraphQL Member dataclasses."""
        return [cls.to_graphql(item) for item in sources if item is not None]  # type: ignore
