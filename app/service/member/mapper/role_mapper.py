"""
Role domain mappers.
Transforms identity.role domain models into authoritative GraphQL response dataclasses.
"""
from __future__ import annotations

from questengine.registry.types import Role as RoleGraphQL

from app.model.identity.role import Role


class RoleMapper:
    """Transforms identity.role models into GraphQL schema type dataclasses."""

    @staticmethod
    def to_graphql(source: Role | None) -> RoleGraphQL | None:
        """Map a Role ORM entity to the generated GraphQL Role dataclass."""
        if source is None:
            return None

        return RoleGraphQL(
            id=str(source.id),
            name=source.name,
            description=source.description,
        )


    @classmethod
    def to_graphql_list(cls, sources: list[Role]) -> list[RoleGraphQL]:
        """Map a list of Role ORM entities to GraphQL Role dataclasses."""
        return [cls.to_graphql(r) for r in sources if r is not None]  # type: ignore
