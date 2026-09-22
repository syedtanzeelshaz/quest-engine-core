from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    """Request body for user registration."""
    email: EmailStr
    password: str
    first_name: str
    last_name: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("This field must not be blank.")
        return v.strip()


class LoginRequest(BaseModel):
    """Request body for user login."""
    email: EmailStr
    password: str


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
    tokens: TokenResponse


class UserPublicProfile(BaseModel):
    """Public-safe view of a user account."""
    user_id: int
    email: str
    first_name: str | None
    last_name: str | None
    status: str
