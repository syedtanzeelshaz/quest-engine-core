"""User domain GraphQL input types."""
from datetime import date

import strawberry

from app.graphql.common.enums import CountryCode, Gender


@strawberry.input(description="Input payload for updating the authenticated user's profile.")
class UpdateUserProfileInput:
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    country: CountryCode | None = None
    gender: Gender | None = None
    date_of_birth: date | None = None
