from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Request model for user registration."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")


class UserResponse(BaseModel):
    """Response model for user data."""

    id: str
    username: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class RegistrationResponse(BaseModel):
    """Response model for user registration."""

    status: str
    message: str


class TokenResponse(BaseModel):
    """Response model for token generation."""

    access_token: str
    token_type: str = "bearer"


class PasswordChange(BaseModel):
    """Request model for password change."""

    old_password: str = Field(..., min_length=8, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class PasswordReset(BaseModel):
    """Request model for password reset (admin)."""

    new_password: str = Field(..., min_length=8, description="New password")


class UserUpdate(BaseModel):
    """Request model for updating user information."""

    username: str | None = Field(
        None, min_length=3, max_length=50, description="New username"
    )


class MessageResponse(BaseModel):
    """Generic message response."""

    status: str
    message: str
