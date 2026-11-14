"""
Member domain service.
Handles member profile retrieval, validations, and profile update logic.
Directly accepts generated GraphQL inputs from questengine.registry.types.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from questengine.registry.types import MemberUpdateInput

from app.core.primitives.exceptions import MemberNotFoundError
from app.model.identity.member import Member
from app.repository.identity.member_repo import MemberRepository


class MemberService:
    """Service encapsulating member domain business logic."""

    def __init__(self, member_repo: MemberRepository) -> None:
        self.member_repo = member_repo

    async def get_member(self, member_id: int) -> Member | None:
        """Fetch a member with roles by member ID."""
        return await self.member_repo.find_by_id_with_roles(member_id)

    async def update_member(self, member_id: int, input_data: MemberUpdateInput) -> Member:
        """
        Update member profile fields using the authoritative MemberUpdateInput contract.
        Raises MemberNotFoundError if the member does not exist.
        """
        member = await self.member_repo.find_by_id_with_roles(member_id)
        if member is None:
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
        return updated_member
