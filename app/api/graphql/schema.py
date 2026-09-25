"""
Root GraphQL schema composition.

Aggregates all domain DataFetchers into Query and all domain DataMutators into Mutation.
"""
import strawberry

from app.api.graphql.organization.organization_data_fetcher import (
    OrganizationDataFetcher,
)
from app.api.graphql.organization.organization_data_mutator import (
    OrganizationDataMutator,
)
from app.api.graphql.user.user_data_fetcher import UserDataFetcher
from app.api.graphql.user.user_data_mutator import UserDataMutator


@strawberry.type
class Query(
    UserDataFetcher,
    OrganizationDataFetcher,
):
    @strawberry.field(description="Health and connectivity check for GraphQL API.")
    def ping(self) -> str:
        return "pong"


@strawberry.type
class Mutation(
    UserDataMutator,
    OrganizationDataMutator,
):
    @strawberry.mutation(description="Health and connectivity check for GraphQL API.")
    def ping(self) -> str:
        return "pong"


schema = strawberry.Schema(query=Query, mutation=Mutation)
