from datetime import timedelta, datetime, timezone
from typing import Any

from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, Field

from ..data.user import get_user_by_username, create_user
from ..settings import AuthSettings
from .status import InternalStatus

auth_settings = AuthSettings()  # type: ignore

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserPayload(BaseModel):
    username: str = Field(..., description="username included in the payload")
    exp: datetime = Field(..., description="The expiration time of the token")


def get_hash(plain: str) -> str:
    return pwd_context.hash(plain)


def get_jwt_username(token: str) -> str:
    """Attempts to retrieve username from payload raises JWTError if no username found or decoding fails"""
    payload = UserPayload(
        **jwt.decode(
            token, auth_settings.SECRET_KEY, algorithms=[auth_settings.ALGORITHM]
        )
    )
    username = payload.username
    if not username:
        raise JWTError
    return username


def verify_credentials(name: str, plain: str) -> InternalStatus:
    """Retrieves user by username and verifies its hashed password against provided one"""
    user = get_user_by_username(name)
    if not user:
        return InternalStatus.USER_NOT_FOUND

    if not verify_password(plain, user.password_hash):
        return InternalStatus.WRONG_PASSWORD

    return InternalStatus.SUCCESS


def verify_password(plain: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain, hashed_password)


def create_jwt_token(username: str) -> str:
    """Generate a JWT token for a user using provided username, secret key, and expiry."""
    payload = create_payload(username)
    encoded_jwt = jwt.encode(
        payload, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM
    )
    return encoded_jwt


def create_payload(username: str) -> dict[str, Any]:
    """Crafts a payload for the jwt token"""
    now_utc = datetime.now(timezone.utc)
    exp = now_utc + timedelta(auth_settings.expire)
    return UserPayload(username=username, exp=exp).model_dump()


def register_user(username: str, plain_password: str) -> InternalStatus:
    """Attempts to create user with the given username"""
    # check whether a user with the given username already exists
    user = get_user_by_username(username)
    if not user:
        password_hash = get_hash(plain_password)
        create_user(username, password_hash)
        return InternalStatus.SUCCESS
    else:
        return InternalStatus.USER_ALREADY_EXISTS
