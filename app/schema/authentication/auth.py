from typing import Self

from pydantic import BaseModel, EmailStr, SecretStr, field_validator, model_validator

from app.core.primitives.enums import Experience


class RegisterRequest(BaseModel):
    """Request body for user registration."""
    email: EmailStr
    password: SecretStr
    confirm_password: SecretStr
    first_name: str
    last_name: str


    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: SecretStr) -> SecretStr:
        secret = v.get_secret_value()
        if len(secret) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if len(secret) > 64 or len(secret.encode("utf-8")) > 72:
            raise ValueError("Password cannot exceed 64 characters.")
        if not any(c.isupper() for c in secret):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in secret):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in secret):
            raise ValueError("Password must contain at least one digit.")
        if not any(not c.isalnum() for c in secret):
            raise ValueError("Password must contain at least one special character.")
        return v


    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("This field must not be blank.")
        if len(stripped) > 100:
            raise ValueError("This field cannot exceed 100 characters.")
        return stripped


    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        if self.password.get_secret_value() != self.confirm_password.get_secret_value():
            raise ValueError("Passwords do not match.")
        return self


class LoginRequest(BaseModel):
    """Request body for user login."""
    email: EmailStr
    password: SecretStr


class RefreshRequest(BaseModel):
    """Request body for token refresh."""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Request body for logout (revokes the provided refresh token)."""
    refresh_token: str


class TokenResponse(BaseModel):
    """JWT token pair returned on login or token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # access token TTL in seconds


class RegisterResponse(BaseModel):
    """Response returned on successful registration."""
    user_id: int
    email: str
    first_name: str | None
    last_name: str | None
    experience: Experience
    tokens: TokenResponse
