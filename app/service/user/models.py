"""
User domain internal models and value objects.

Pure Python dataclasses representing user identity and caller context.
"""
from dataclasses import dataclass
from enum import StrEnum


class AdminRole(StrEnum):
    """Administrator roles capable of managing organization-scoped resources."""
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"


@dataclass(frozen=True)
class CurrentUser:
    """
    Authenticated caller identity context.

    Propagated across request handlers, GraphQL context, authorization guards,
    and domain service layers.
    """
    id: int
    email: str
    first_name: str | None = None
    last_name: str | None = None
    org_id: int | None = None
    roles: tuple[str, ...] = ()

