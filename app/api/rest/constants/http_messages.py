"""HTTP response message constants for REST API responses."""


class HttpMessage:
    # Authentication
    EMAIL_ALREADY_REGISTERED = "Email already registered"
    INVALID_CREDENTIALS = "Invalid credentials"
    ACCOUNT_NOT_ACTIVE = "Account not active"
    AUTHENTICATION_REQUIRED = "Authentication required"
    INVALID_TOKEN = "Invalid token"
    INVALID_REFRESH_TOKEN = "Invalid refresh token"
    LOGOUT_SUCCESSFUL = "Logout successful"

    # General
    NOT_FOUND = "Not found"
    INTERNAL_SERVER_ERROR = "Internal server error"

