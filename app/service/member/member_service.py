"""
Member domain service.
Handles member profile retrieval, validations, profile updates, and role resolution.
Directly accepts generated GraphQL inputs and returns generated GraphQL response types.
"""
from __future__ import annotations

from datetime import date

from questengine.registry.types import (
    Member as MemberGraphQL,
    MemberUpdateInput,
    Role as RoleGraphQL,
)

from app.core.primitives.exceptions import MemberNotFoundError
from app.repository.identity.member_repo import MemberRepository
from app.repository.identity.role_repo import RoleRepository
from app.service.member.mapper import MemberMapper, RoleMapper
from app.util.logger import log


class MemberService:
    """Service encapsulating member domain business logic."""

    def __init__(
        self,
        member_repo: MemberRepository,
        role_repo: RoleRepository | None = None,
    ) -> None:
        self.member_repo = member_repo
        self.role_repo = role_repo if role_repo is not None else RoleRepository()


    async def get_member(self, member_id: int) -> MemberGraphQL | None:
        """Fetch a member by member ID and map to GraphQL response type."""
        log.info("Fetching member profile for memberId: %d", member_id)

        member = await self.member_repo.find_by_id(member_id)
        if member is None:
            log.warning("Member not found for memberId: %d", member_id)
            return None

        return MemberMapper.to_graphql(member)


    async def get_members_batch(self, member_ids: list[int]) -> dict[int, MemberGraphQL]:
        """Batch-fetch members by IDs and map to GraphQL Member dataclasses."""
        log.info("Fetching batch of %d members for memberIds: %s", len(member_ids), member_ids)

        members = await self.member_repo.find_all_by_ids(member_ids)

        return {
            m.id: MemberMapper.to_graphql(m)  # type: ignore
            for m in members
            if m.id is not None
        }


    async def update_member(self, member_id: int, input_data: MemberUpdateInput) -> MemberGraphQL:
        """
        Update member profile fields using the authoritative MemberUpdateInput contract.
        Raises MemberNotFoundError if the member does not exist.
        """
        log.info("Updating profile details for memberId: %d", member_id)

        member = await self.member_repo.find_by_id(member_id)
        if member is None:
            log.error("Member not found for update, memberId: %d", member_id)
            raise MemberNotFoundError(f"Member with id {member_id} not found.")

        if input_data.firstName is not None:
            member.first_name = input_data.firstName.strip() or None

        if input_data.lastName is not None:
            member.last_name = input_data.lastName.strip() or None

        if input_data.phone is not None:
            member.phone = input_data.phone.strip() or None

        if input_data.country is not None:
            member.country = input_data.country.strip() or None

        if input_data.gender is not None:
            member.gender = input_data.gender.strip() or None

        if input_data.dateOfBirth is not None:
            if isinstance(input_data.dateOfBirth, str):
                member.date_of_birth = date.fromisoformat(input_data.dateOfBirth)
            elif isinstance(input_data.dateOfBirth, date):
                member.date_of_birth = input_data.dateOfBirth

        updated_member = await self.member_repo.save_and_flush(member)
        log.info("Successfully updated member profile for memberId: %d", member_id)

        return MemberMapper.to_graphql(updated_member)  # type: ignore


    async def get_roles_for_member(self, member_id: int) -> list[RoleGraphQL]:
        """Fetch roles for a specific member and map to GraphQL Role dataclasses."""
        log.info("Fetching roles for memberId: %d", member_id)

        roles = await self.role_repo.find_roles_by_member_id(member_id)

        return RoleMapper.to_graphql_list(roles)


    async def get_roles_for_members_batch(self, member_ids: list[int]) -> dict[int, list[RoleGraphQL]]:
        """Batch-fetch roles for members and map to GraphQL Role dataclasses."""
        log.info("Fetching batch roles for %d members: %s", len(member_ids), member_ids)

        grouped_roles = await self.role_repo.find_roles_by_member_ids(member_ids)

        return {
            mid: RoleMapper.to_graphql_list(roles)
            for mid, roles in grouped_roles.items()
        }
