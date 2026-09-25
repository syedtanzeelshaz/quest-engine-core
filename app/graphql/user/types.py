"""User domain GraphQL output types."""
from datetime import date, datetime

import strawberry

from app.graphql.common.enums import CountryCode, Gender
from app.graphql.user.enums import AppUserStatus


@strawberry.type(name="User", description="Application user representation.")
class UserType:
    id: strawberry.ID
    email: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    country: CountryCode | None = None
    gender: Gender | None = None
    date_of_birth: date | None = None
    status: AppUserStatus | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
