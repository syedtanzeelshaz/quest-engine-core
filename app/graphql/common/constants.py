"""
GraphQL shared constants.
"""

DEFAULT_SCHEMA_OUTPUT_PATH = "schema-package/schema.graphql"
GRAPHIQL_IDE = "graphiql"


class GraphQLMessage:
    """Standard GraphQL error and status messages."""
    AUTHENTICATION_REQUIRED = "Authentication required."
    ORGANIZATION_MEMBERSHIP_REQUIRED = "Organization membership required."
    ADMIN_ACCESS_REQUIRED = "Admin access required."
