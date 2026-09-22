"""HTTP response message constants for REST API responses."""


class HttpMessage:
    # Authentication
    EMAIL_ALREADY_REGISTERED = "Email address is already registered."
    INVALID_CREDENTIALS = "Invalid email or password."
    ACCOUNT_NOT_ACTIVE = "Account is not active. Please contact support."
    AUTHENTICATION_REQUIRED = "Authentication required."
    INVALID_TOKEN = "Token is invalid or expired."
    INVALID_REFRESH_TOKEN = "Refresh token is invalid, expired, or already revoked."
    LOGOUT_SUCCESSFUL = "Successfully logged out."

    # General
    NOT_FOUND = "The requested resource was not found."
    INTERNAL_ERROR = "An unexpected error occurred. Please try again later."
