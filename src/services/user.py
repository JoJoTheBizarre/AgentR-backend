"""
Authentication Service Layer
Handles business logic for user authentication, registration, and JWT operations.
"""

from datetime import timedelta, datetime, timezone
from typing import Any

from jose import jwt
from jose.exceptions import JWTError
import uuid
from passlib.context import CryptContext
from pydantic import BaseModel, Field

from src.repositories.user import get_user_by_username, create_user, user_exists
from src.models import User
from src.settings import AuthSettings
from src.services.status import InternalStatus

_auth_settings_cache: AuthSettings | None = None


def get_auth_settings() -> AuthSettings:
    """Get cached AuthSettings instance."""
    global _auth_settings_cache
    if _auth_settings_cache is None:
        _auth_settings_cache = AuthSettings()  # type: ignore
    return _auth_settings_cache


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTPayload(BaseModel):
    """JWT token payload structure."""

    username: str = Field(..., description="Username included in the payload")
    exp: datetime = Field(..., description="The expiration time of the token")


def hash_password(plain_password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_jwt_username(token: str) -> str:
    """Extract and validate username from JWT token."""
    try:
        payload = jwt.decode(
            token,
            get_auth_settings().SECRET_KEY,
            algorithms=[get_auth_settings().ALGORITHM],
        )

        # Validate payload structure
        jwt_payload = JWTPayload(**payload)

        if not jwt_payload.username:
            raise JWTError("Username not found in token")

        return jwt_payload.username

    except Exception as e:
        raise JWTError(f"Invalid token: {str(e)}")


def create_jwt_payload(username: str) -> dict[str, Any]:
    """Create a JWT payload dictionary."""
    now_utc = datetime.now(timezone.utc)
    exp = now_utc + timedelta(minutes=get_auth_settings().token_expire_minutes)
    return JWTPayload(username=username, exp=exp).model_dump()


def create_jwt_token(username: str) -> str:
    """Generate a JWT token for a user."""
    payload = create_jwt_payload(username)
    encoded_jwt = jwt.encode(
        payload, get_auth_settings().SECRET_KEY, algorithm=get_auth_settings().ALGORITHM
    )
    return encoded_jwt


def verify_credentials(username: str, plain_password: str) -> InternalStatus:
    """Verify user credentials by checking username and password."""
    user = get_user_by_username(username)

    if not user:
        return InternalStatus.USER_NOT_FOUND

    if not verify_password(plain_password, user.password_hash):
        return InternalStatus.WRONG_PASSWORD

    return InternalStatus.SUCCESS


def register_user(
    username: str, plain_password: str, email: str | None = None
) -> InternalStatus:
    """Register a new user with the given credentials."""
    if user_exists(username):
        return InternalStatus.USER_ALREADY_EXISTS

    user = User(
        id=uuid.uuid4(),
        username=username,
        password_hash=hash_password(plain_password),
    )

    create_user(user)
    return InternalStatus.SUCCESS


def authenticate_user(
    username: str, plain_password: str
) -> tuple[InternalStatus, str | None]:
    """Authenticate user and generate JWT token if successful."""
    status = verify_credentials(username, plain_password)

    if status != InternalStatus.SUCCESS:
        return status, None

    token = create_jwt_token(username)
    return InternalStatus.SUCCESS, token


def verify_jwt_token(token: str) -> tuple[bool, str | None]:
    """Verify JWT token and return username if valid."""
    try:
        username = get_jwt_username(token)
        return True, username
    except JWTError:
        return False, None


def get_user_from_token(token: str) -> User | None:
    """Get user object from JWT token."""
    try:
        username = get_jwt_username(token)
        return get_user_by_username(username)
    except JWTError:
        return None
