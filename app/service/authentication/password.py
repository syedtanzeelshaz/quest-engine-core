"""
PasswordService — bcrypt password hashing and verification.

Pure utility class with no I/O or database access.
Fully unit-testable in isolation.
"""
import bcrypt


class PasswordService:
    """Handles secure password hashing and verification using bcrypt."""

    def hash(self, plain_password: str) -> str:
        """Hash a plain-text password using bcrypt. Returns the hashed string."""
        pwd_bytes = plain_password.encode("utf-8")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain-text password against a bcrypt hash.
        Returns True if they match, False otherwise.
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception:
            return False
