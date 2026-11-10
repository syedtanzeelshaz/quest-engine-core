"""
Protocol-agnostic API error sanitizers.

Sanitizes error payloads to ensure sensitive credentials (passwords, tokens,
secrets) are stripped before serialization into responses, client logs, or APM tools.
"""
from typing import Any


def sanitize_validation_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Sanitize validation error dictionaries by stripping the raw 'input' field.

    Safe for consumption by REST JSONResponse handlers, GraphQL error extensions,
    and WebSocket error frames.
    """
    sanitized: list[dict[str, Any]] = []
    for error in errors:
        clean_error = dict(error)
        clean_error.pop("input", None)
        sanitized.append(clean_error)
    return sanitized

