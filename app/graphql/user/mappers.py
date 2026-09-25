"""User domain translation mappers: ORM entity -> GraphQL type."""
import strawberry

from app.graphql.user.types import UserType
from app.model.identity.app_user import AppUser


def user_to_type(user: AppUser) -> UserType:
    """
    Pure translation function mapping an AppUser ORM model to a UserType GraphQL instance.
    Does not perform any I/O or database queries.
    """
    return UserType(
        id=strawberry.ID(str(user.id)),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        country=user.country,
        gender=user.gender,
        date_of_birth=user.date_of_birth,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
