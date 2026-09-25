"""User domain GraphQL enums."""
import strawberry

from app.model.identity.app_user import AppUserStatus

strawberry.enum(
    AppUserStatus,
    name="AppUserStatus",
    description="Account lifecycle status for an application user.",
)

__all__ = ["AppUserStatus"]
