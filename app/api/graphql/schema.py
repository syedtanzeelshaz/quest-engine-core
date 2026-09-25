"""
Root GraphQL schema composition.

Aggregates all domain DataFetchers into Query and all domain DataMutators into Mutation.
"""
import strawberry


@strawberry.type
class Query:
    @strawberry.field(description="Health and connectivity check for GraphQL API.")
    def ping(self) -> str:
        return "pong"


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Placeholder mutation until domain mutators are registered.")
    def ping(self) -> str:
        return "pong"


schema = strawberry.Schema(query=Query, mutation=Mutation)
