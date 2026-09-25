"""User domain GraphQL input types."""
from datetime import date

import strawberry


@strawberry.input(description="Input payload for updating the authenticated user's profile.")
class UpdateUserProfileInput:
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    country: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None
