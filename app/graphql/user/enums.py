"""User domain GraphQL enums."""
from enum import StrEnum

import strawberry

from app.model.identity.app_user import AppUserStatus


@strawberry.enum(name="UserStatus", description="Account lifecycle status for an application user.")
class UserStatusEnum(StrEnum):
    ACTIVE = AppUserStatus.ACTIVE.value
    INACTIVE = AppUserStatus.INACTIVE.value
    SUSPENDED = AppUserStatus.SUSPENDED.value
    DELETED = AppUserStatus.DELETED.value
