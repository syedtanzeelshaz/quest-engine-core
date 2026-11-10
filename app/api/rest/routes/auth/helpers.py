"""
Shared helper utilities for authentication REST routes.
"""
from app.schema.authentication.auth import TokenResponse
from app.service.authentication.models import AuthTokenPair


def make_token_response(token_pair: AuthTokenPair) -> TokenResponse:
    """Format an internal AuthTokenPair value object into an API TokenResponse schema."""
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        expires_in=token_pair.expires_in,
    )

