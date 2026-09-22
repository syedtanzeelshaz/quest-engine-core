"""
PasswordService — bcrypt password hashing and verification.

Pure utility class with no I/O or database access.
Fully unit-testable in isolation.
"""
from passlib.context import CryptContext

_crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
    """Handles secure password hashing and verification using bcrypt."""

    def hash(self, plain_password: str) -> str:
        """Hash a plain-text password using bcrypt. Returns the hashed string."""
        return _crypt_context.hash(plain_password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain-text password against a bcrypt hash.
        Returns True if they match, False otherwise.
        """
        return _crypt_context.verify(plain_password, hashed_password)
