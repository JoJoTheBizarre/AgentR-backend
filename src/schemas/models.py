from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration request."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for OAuth2 token response."""

    access_token: str
    token_type: str = "bearer"


class RegistrationResponse(BaseModel):
    """Schema for user registration response."""

    status: str
    user_id: Optional[str] = None
    username: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str
