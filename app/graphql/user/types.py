"""User domain GraphQL output types."""
from datetime import date, datetime

import strawberry

from app.graphql.user import enums  # noqa: F401 - ensures GraphQL enum registration
from app.model.identity.app_user import AppUserStatus


@strawberry.type(name="User", description="Application user representation.")
class UserType:
    id: strawberry.ID
    email: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    country: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    status: AppUserStatus | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
