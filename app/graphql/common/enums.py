"""Common domain GraphQL enums."""
import strawberry

from app.core.enums import CountryCode, Gender

strawberry.enum(
    Gender,
    name="Gender",
    description="User gender identity options.",
)

strawberry.enum(
    CountryCode,
    name="CountryCode",
    description="ISO 3166-1 alpha-3 three-letter country codes.",
)

__all__ = [
    "CountryCode",
    "Gender",
]
