"""Organization domain translation mappers: ORM entity -> GraphQL type."""
import strawberry

from app.graphql.organization.types import OrganizationType
from app.model.identity.organization import Organization


def organization_to_type(org: Organization) -> OrganizationType:
    """
    Pure translation function mapping an Organization ORM model to an OrganizationType GraphQL instance.
    Does not perform any I/O or database queries.
    """
    return OrganizationType(
        id=strawberry.ID(str(org.id)),
        name=org.name,
        slug=org.slug,
        description=org.description,
        status=org.status,
        created_at=org.created_at,
        updated_at=org.updated_at,
    )
