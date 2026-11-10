"""
API layer exception handlers.

Registers global FastAPI application-level exception handlers and sanitizers.
Protects against credential leakage and formats validation responses across the API layer.
"""
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.rest.constants.http_codes import HttpCode
from app.api.sanitizers import sanitize_validation_errors


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Sanitize 422 validation errors by stripping the raw 'input' field.

    Prevents sensitive user input (such as passwords and credentials)
    from leaking into error response bodies, client logs, or APM tools.
    """
    sanitized_errors = sanitize_validation_errors(exc.errors())
    return JSONResponse(
        status_code=HttpCode._422,
        content={"detail": jsonable_encoder(sanitized_errors)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global API exception handlers with the FastAPI application."""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

