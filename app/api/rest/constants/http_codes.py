"""HTTP status code constants for REST API responses."""


class HttpCode:
    # 2xx Success
    _200 = 200  # OK: Request succeeded
    _201 = 201  # Created: Resource successfully created

    # 4xx Client Errors
    _400 = 400  # Bad Request: Malformed syntax or invalid request
    _401 = 401  # Unauthorized: Authentication required or failed
    _403 = 403  # Forbidden: Authenticated but not authorized
    _404 = 404  # Not Found: Resource does not exist
    _409 = 409  # Conflict: Request conflicts with current server state
    _422 = 422  # Unprocessable Entity: Validation failed

    # 5xx Server Errors
    _500 = 500  # Internal Server Error: Unexpected server error
