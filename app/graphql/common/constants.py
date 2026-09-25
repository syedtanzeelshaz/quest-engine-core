"""
GraphQL shared constants.
"""

from app.core.constants import SecurityMessage

DEFAULT_SCHEMA_OUTPUT_PATH = "schema-package/schema.graphql"
GRAPHIQL_IDE = "graphiql"
DEFAULT_LOADER_BATCH_SIZE = 100


class GraphQLMessage(SecurityMessage):
    """Standard GraphQL error and status messages."""

