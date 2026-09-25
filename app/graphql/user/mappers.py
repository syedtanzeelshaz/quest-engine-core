"""User domain translation mappers: ORM entity -> GraphQL type."""
import strawberry

from app.graphql.user.enums import UserStatusEnum
from app.graphql.user.types import UserType
from app.model.identity.app_user import AppUser


def user_to_type(user: AppUser) -> UserType:
    """
    Pure translation function mapping an AppUser ORM model to a UserType GraphQL instance.
    Does not perform any I/O or database queries.
    """
    status_enum: UserStatusEnum | None = None
    if user.status is not None:
        try:
            status_val = user.status.value if hasattr(user.status, "value") else str(user.status)
            status_enum = UserStatusEnum(status_val)
        except (ValueError, KeyError):
            status_enum = None

    return UserType(
        id=strawberry.ID(str(user.id)),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        country=user.country,
        gender=user.gender,
        date_of_birth=user.date_of_birth,
        status=status_enum,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
