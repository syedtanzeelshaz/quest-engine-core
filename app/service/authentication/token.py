"""
TokenService — JWT token issuance and verification.

Pure utility class with no I/O or database access.
Handles access and refresh token lifecycle at the cryptographic level only.
Fully unit-testable in isolation.
"""
import hashlib
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import Settings
from app.core.exceptions import InvalidRefreshTokenError
from app.service.authentication.models import AuthTokenPair

_ACCESS_TOKEN_TYPE = "access"
_REFRESH_TOKEN_TYPE = "refresh"


class TokenService:
    """Issues, decodes, and validates JWTs. Does NOT persist anything to DB."""

    def __init__(self, settings: Settings) -> None:
        self._secret = settings.JWT_SECRET_KEY
        self._algorithm = settings.JWT_ALGORITHM
        self._access_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self._refresh_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def issue_pair(
        self,
        user_id: int,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
        roles: list[str] | None = None,
    ) -> AuthTokenPair:
        """
        Issue a signed access + refresh JWT pair for the given user.
        Does NOT store anything in the database.

        Payload structure:
            Access token:
                sub: email
                details: { id: user_id, firstName, lastName }
                roles: list[str] or null (if no organization memberships)
                type: "access"
                iat, exp
            Refresh token:
                sub: email
                user_id: user_id
                type: "refresh"
                iat, exp
        """
        now = datetime.now(timezone.utc)
        access_expire = timedelta(minutes=self._access_expire_minutes)
        refresh_expire = timedelta(days=self._refresh_expire_days)

        access_payload = {
            "sub": email,
            "details": {
                "id": user_id,
                "firstName": first_name or "",
                "lastName": last_name or "",
            },
            "roles": roles,
            "type": _ACCESS_TOKEN_TYPE,
            "iat": now,
            "exp": now + access_expire,
        }

        refresh_payload = {
            "sub": email,
            "user_id": user_id,
            "type": _REFRESH_TOKEN_TYPE,
            "iat": now,
            "exp": now + refresh_expire,
        }

        access_token = jwt.encode(access_payload, self._secret, algorithm=self._algorithm)
        refresh_token = jwt.encode(refresh_payload, self._secret, algorithm=self._algorithm)

        return AuthTokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_expire.total_seconds()),
        )

    def verify_access_token(self, token: str) -> int:
        """
        Decode and validate a JWT access token.
        Returns the user_id if valid.
        Raises InvalidRefreshTokenError on any failure.
        """
        return self._decode_and_validate(token, expected_type=_ACCESS_TOKEN_TYPE)

    def verify_refresh_token(self, token: str) -> int:
        """
        Decode and validate a JWT refresh token.
        Returns the user_id if valid.
        Raises InvalidRefreshTokenError on any failure.
        """
        return self._decode_and_validate(token, expected_type=_REFRESH_TOKEN_TYPE)

    def decode_token(self, token: str) -> dict:
        """Decode and return the full raw JWT payload."""
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except JWTError:
            raise InvalidRefreshTokenError("Token is invalid or expired.")

    def refresh_token_expires_at(self) -> datetime:
        """Return the absolute expiry datetime for a newly issued refresh token."""
        return datetime.now(timezone.utc) + timedelta(days=self._refresh_expire_days)

    @staticmethod
    def hash_token(raw_token: str) -> str:
        """SHA-256 hash a raw JWT string for safe DB storage (64 hex chars)."""
        return hashlib.sha256(raw_token.encode()).hexdigest()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _decode_and_validate(self, token: str, expected_type: str) -> int:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except JWTError:
            raise InvalidRefreshTokenError("Token is invalid or expired.")

        token_type = payload.get("type")
        if token_type != expected_type:
            raise InvalidRefreshTokenError(
                f"Expected token type '{expected_type}', got '{token_type}'."
            )

        user_id = None
        details = payload.get("details")
        if isinstance(details, dict) and "id" in details:
            user_id = details["id"]
        elif "user_id" in payload:
            user_id = payload["user_id"]
        else:
            sub = payload.get("sub")
            if sub is not None:
                try:
                    user_id = int(sub)
                except (ValueError, TypeError):
                    pass

        if user_id is None:
            raise InvalidRefreshTokenError("Token user identifier is missing.")

        try:
            return int(user_id)
        except (ValueError, TypeError):
            raise InvalidRefreshTokenError("Token user identifier is not a valid integer.")

