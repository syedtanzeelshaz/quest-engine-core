"""
Member service factory.

Pure Python factory functions to construct member domain services.
Completely framework-agnostic (zero FastAPI/GraphQL imports). Safe to use across REST,
GraphQL, WebSocket, background tasks, CLI scripts, and unit tests.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.identity.member_repo import MemberRepository
from app.service.member.member_service import MemberService


def build_member_service(session: AsyncSession | None = None) -> MemberService:
    """Construct a MemberService wired with MemberRepository."""
    return MemberService(
        member_repo=MemberRepository(session),
    )
