"""
Member GraphQL presentation module.
Exports query fetchers, mutation mutators, and object type loaders.
"""
from app.api.graphql.member.member_data_fetcher import member_query
from app.api.graphql.member.member_data_loader import member_type, role_type
from app.api.graphql.member.member_data_mutator import member_mutation

MEMBER_RESOLVERS = [
    member_query,
    member_mutation,
    member_type,
    role_type,
]

__all__ = [
    "MEMBER_RESOLVERS",
    "member_mutation",
    "member_query",
    "member_type",
    "role_type",
]
