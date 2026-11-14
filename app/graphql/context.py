"""
GraphQL per-request execution context.
"""
from __future__ import annotations

from dataclasses import dataclass
from starlette.requests import Request

from app.core.primitives.enums import Experience
from app.service.user.models import CurrentUser


@dataclass
class GraphQLContext:
    """
    Per-request execution context accessible across all GraphQL resolvers and directives.
    Delegates identity, experience, and permissions directly to the CurrentUser principal.
    """
    request: Request
    caller: CurrentUser | None = None

    @property
    def is_authenticated(self) -> bool:
        """Check if request contains an active authenticated caller."""
        return self.caller is not None and self.caller.is_active

    @property
    def experience(self) -> Experience:
        """Active experience context from caller or defaults to CUSTOMER."""
        return self.caller.experience if self.caller else Experience.CUSTOMER

    @property
    def permissions(self) -> set[str]:
        """Assigned permissions from caller principal."""
        return self.caller.permissions if self.caller else set()
