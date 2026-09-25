"""Organization domain GraphQL input types."""
import strawberry


@strawberry.input(description="Input payload for creating a new tenant organization.")
class CreateOrganizationInput:
    name: str
    slug: str
    description: str | None = None


@strawberry.input(description="Input payload for updating organization details.")
class UpdateOrganizationInput:
    name: str | None = None
    description: str | None = None
