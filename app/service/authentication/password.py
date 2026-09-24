"""
PasswordService — bcrypt password hashing and verification.

CPU-bound bcrypt operations are offloaded to worker threads via asyncio.to_thread
to prevent blocking the asynchronous event loop.
"""
import asyncio

import bcrypt


class PasswordService:
    """Handles secure password hashing and verification using bcrypt."""

    async def hash(self, plain_password: str) -> str:
        """Hash a plain-text password using bcrypt offloaded to a worker thread."""
        return await asyncio.to_thread(self._compute_hash, plain_password)

    async def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain-text password against a bcrypt hash offloaded to a worker thread."""
        return await asyncio.to_thread(self._check_password, plain_password, hashed_password)

    @staticmethod
    def _compute_hash(plain_password: str) -> str:
        # CPU-intensive key derivation and salting
        pwd_bytes = plain_password.encode("utf-8")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

    @staticmethod
    def _check_password(plain_password: str, hashed_password: str) -> bool:
        # CPU-intensive bcrypt hash verification
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception:
            return False
