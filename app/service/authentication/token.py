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

    def issue_pair(self, user_id: int) -> AuthTokenPair:
        """
        Issue a signed access + refresh JWT pair for the given user ID.
        Does NOT store anything in the database.
        """
        now = datetime.now(timezone.utc)
        access_expire = timedelta(minutes=self._access_expire_minutes)
        refresh_expire = timedelta(days=self._refresh_expire_days)

        access_token = self._encode(
            user_id=user_id,
            token_type=_ACCESS_TOKEN_TYPE,
            expires_delta=access_expire,
            now=now,
        )
        refresh_token = self._encode(
            user_id=user_id,
            token_type=_REFRESH_TOKEN_TYPE,
            expires_delta=refresh_expire,
            now=now,
        )
        return AuthTokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_expire.total_seconds()),
        )

    def verify_access_token(self, token: str) -> int:
        """
        Decode and validate a JWT access token.
        Returns the user_id (subject) if valid.
        Raises InvalidRefreshTokenError on any failure.
        """
        return self._decode_and_validate(token, expected_type=_ACCESS_TOKEN_TYPE)

    def verify_refresh_token(self, token: str) -> int:
        """
        Decode and validate a JWT refresh token.
        Returns the user_id (subject) if valid.
        Raises InvalidRefreshTokenError on any failure.
        """
        return self._decode_and_validate(token, expected_type=_REFRESH_TOKEN_TYPE)

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

    def _encode(
        self,
        user_id: int,
        token_type: str,
        expires_delta: timedelta,
        now: datetime,
    ) -> str:
        payload = {
            "sub": str(user_id),
            "type": token_type,
            "iat": now,
            "exp": now + expires_delta,
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

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

        sub = payload.get("sub")
        if sub is None:
            raise InvalidRefreshTokenError("Token subject (user_id) is missing.")

        try:
            return int(sub)
        except (ValueError, TypeError):
            raise InvalidRefreshTokenError("Token subject is not a valid user ID.")
