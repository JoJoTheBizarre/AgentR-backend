from datetime import timedelta, datetime, timezone
from typing import Any

from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from pydantic import BaseModel, Field

from src.db.models import User
from src.settings import AuthSettings
from src.services.status import InternalStatus, Result
from src.services.user import UserService


class JWTPayload(BaseModel):
    """JWT token payload structure."""

    username: str = Field(..., description="Username included in the payload")
    exp: datetime = Field(..., description="The expiration time of the token")


class AuthenticationService:
    """Handles user authentication, JWT operations, and password verification."""

    def __init__(
        self,
        settings: AuthSettings | None = None,
        user_service: UserService | None = None,
    ):
        """Initialize authentication service with settings and user service."""
        self.settings = settings or AuthSettings()  # type: ignore
        self.user_service = user_service or UserService()

    def create_jwt_payload(self, username: str) -> dict[str, Any]:
        """Create a JWT payload dictionary."""
        now_utc = datetime.now(timezone.utc)
        exp = now_utc + timedelta(minutes=self.settings.token_expire_minutes)
        return JWTPayload(username=username, exp=exp).model_dump()

    def create_jwt_token(self, username: str) -> str:
        """Generate a JWT token for a user."""
        payload = self.create_jwt_payload(username)
        encoded_jwt = jwt.encode(
            payload, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM
        )
        return encoded_jwt

    def get_jwt_username(self, token: str) -> Result[str]:
        """Extract and validate username from JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.settings.SECRET_KEY,
                algorithms=[self.settings.ALGORITHM],
            )

            jwt_payload = JWTPayload(**payload)

            if not jwt_payload.username:
                return Result.failure(
                    InternalStatus.INVALID_TOKEN, "Username not found in token"
                )

            return Result.success(jwt_payload.username)

        except ExpiredSignatureError:
            return Result.failure(InternalStatus.TOKEN_EXPIRED, "Token has expired")
        except JWTError as e:
            return Result.failure(
                InternalStatus.INVALID_TOKEN, f"Invalid token: {str(e)}"
            )
        except Exception as e:
            return Result.failure(
                InternalStatus.INVALID_TOKEN, f"Token validation error: {str(e)}"
            )

    def verify_jwt_token(self, token: str) -> Result[str]:
        """Verify JWT token and return username if valid."""
        return self.get_jwt_username(token)

    def verify_credentials(self, username: str, plain_password: str) -> Result[User]:
        """Verify user credentials by checking username and password."""
        # Use UserService to get user
        user_result = self.user_service.get_user_by_username(username)

        if user_result.is_failure:
            return Result.failure(
                InternalStatus.USER_NOT_FOUND, f"User '{username}' not found"
            )

        user = user_result.data

        if not self.user_service.verify_password(plain_password, user.password_hash):  # type: ignore
            return Result.failure(InternalStatus.WRONG_PASSWORD, "Invalid password")

        return Result.success(user, "Credentials verified")

    def authenticate_user(self, username: str, plain_password: str) -> Result[str]:
        """Authenticate user and generate JWT token if successful."""
        credentials_result = self.verify_credentials(username, plain_password)

        if credentials_result.is_failure:
            return Result.failure(credentials_result.status, credentials_result.message)

        token = self.create_jwt_token(username)
        return Result.success(token, "Authentication successful")

    def get_user_from_token(self, token: str) -> Result[User]:
        """Get user object from JWT token."""
        username_result = self.get_jwt_username(token)

        if username_result.is_failure:
            return Result.failure(username_result.status, username_result.message)

        user_result = self.user_service.get_user_by_username(username_result.data)  # type: ignore

        if user_result.is_failure:
            return Result.failure(
                InternalStatus.USER_NOT_FOUND, "User associated with token not found"
            )

        return Result.success(user_result.data, "User retrieved from token")

    def refresh_token(self, old_token: str) -> Result[str]:
        """
        Refresh an expired or soon-to-expire token.

        Args:
            old_token: The token to refresh

        Returns:
            Result containing new token or error status
        """
        username_result = self.get_jwt_username(old_token)

        if username_result.is_failure:
            # Allow refresh even if token is expired
            if username_result.status != InternalStatus.TOKEN_EXPIRED:
                return Result.failure(username_result.status, username_result.message)

            # For expired tokens, we need to decode without verification
            # This is safe for refresh operations
            try:
                payload = jwt.decode(
                    old_token,
                    self.settings.SECRET_KEY,
                    algorithms=[self.settings.ALGORITHM],
                    options={"verify_exp": False},
                )
                username = payload.get("username")

                if not username:
                    return Result.failure(
                        InternalStatus.INVALID_TOKEN,
                        "Username not found in expired token",
                    )
            except JWTError as e:
                return Result.failure(
                    InternalStatus.INVALID_TOKEN,
                    f"Cannot refresh invalid token: {str(e)}",
                )
        else:
            username = username_result.data

        # Verify user still exists
        user_result = self.user_service.get_user_by_username(username)  # type: ignore

        if user_result.is_failure:
            return Result.failure(
                InternalStatus.USER_NOT_FOUND, f"User '{username}' no longer exists"
            )

        # Generate new token
        new_token = self.create_jwt_token(username)  # type: ignore
        return Result.success(new_token, "Token refreshed successfully")
