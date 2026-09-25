"""
Core shared domain constants grouped by domain.
"""


class SecurityMessage:
    """Security, identity, and authorization messages."""

    AUTHENTICATION_REQUIRED = "Authentication required."
    ORGANIZATION_MEMBERSHIP_REQUIRED = "Organization membership required."
    ADMIN_ACCESS_REQUIRED = "Admin access required."


class UserMessage:
    """User domain messages."""

    USER_NOT_FOUND = "User not found."


class OrganizationMessage:
    """Organization domain messages."""

    ORGANIZATION_NOT_FOUND = "Organization not found."
    SLUG_ALREADY_EXISTS = "Slug already exists."
