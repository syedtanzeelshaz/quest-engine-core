"""
User domain value objects and dataclasses.

Pure Python dataclasses representing authenticated user context and scopes.
Safe to share across services, presentation layers, and GraphQL execution context
without leaking sensitive credential attributes (e.g. password_hash).
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from questengine.registry.types import UserStatus

from app.core.primitives.enums import Experience
from app.core.security.permissions import has_any_permission, has_matching_permission


@dataclass(frozen=True)
class UserScopes:
    """Scoped identifiers associated with the current user's active persona."""
    member_id: int | None = None
    org_id: int | None = None
    operator_id: int | None = None


@dataclass(frozen=True)
class CurrentUser:
    """
    Sanitized representation of the currently authenticated principal.

    Contains identity, persona context, roles, permissions, and scope identifiers.
    Omits sensitive security credentials (password hashes, audit revisions).
    """
    id: int
    email: str
    experience: Experience
    status: UserStatus
    first_name: str | None = None
    last_name: str | None = None
    roles: list[str] = field(default_factory=list)
    permissions: set[str] = field(default_factory=set)
    scopes: UserScopes = field(default_factory=UserScopes)


    @property
    def full_name(self) -> str:
        """Formatted full name of the user."""
        return f"{self.first_name or ''} {self.last_name or ''}".strip()


    @property
    def is_active(self) -> bool:
        """Check if user account status is ACTIVE."""
        return self.status == UserStatus.ACTIVE


    @property
    def is_operations(self) -> bool:
        """Check if user experience is OPERATIONS."""
        return self.experience == Experience.OPERATIONS


    @property
    def is_customer(self) -> bool:
        """Check if user experience is CUSTOMER."""
        return self.experience == Experience.CUSTOMER


    @property
    def org_id(self) -> int | None:
        """Convenience accessor for organization ID from scopes."""
        return self.scopes.org_id


    @property
    def member_id(self) -> int | None:
        """Convenience accessor for member ID from scopes."""
        return self.scopes.member_id


    @property
    def operator_id(self) -> int | None:
        """Convenience accessor for operator ID from scopes."""
        return self.scopes.operator_id


    def has_permission(self, permission: str) -> bool:
        """Check if caller's assigned permissions satisfy the required permission string."""
        return has_matching_permission(self.permissions, permission)


    def has_any_permission(self, permissions: Iterable[str]) -> bool:
        """Check if caller's assigned permissions satisfy any of the required permission strings."""
        return has_any_permission(self.permissions, permissions)
