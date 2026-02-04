from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.services.auth import AuthenticationService
from src.services.user import UserService
from src.services.status import InternalStatus
from src.db.models import User
from src.routes.status_message import StatusMessage


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

auth_service = AuthenticationService()
user_service = UserService()


STATUS_CODE_MAP = {
    InternalStatus.SUCCESS: status.HTTP_200_OK,
    InternalStatus.USER_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    InternalStatus.USER_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
    InternalStatus.WRONG_PASSWORD: status.HTTP_401_UNAUTHORIZED,
    InternalStatus.INVALID_TOKEN: status.HTTP_401_UNAUTHORIZED,
    InternalStatus.TOKEN_EXPIRED: status.HTTP_401_UNAUTHORIZED,
    InternalStatus.DB_CONNECTION_FAILED: status.HTTP_503_SERVICE_UNAVAILABLE,
}


STATUS_MESSAGE_MAP = {
    InternalStatus.SUCCESS: StatusMessage.SUCCESS,
    InternalStatus.USER_NOT_FOUND: StatusMessage.USER_NOT_FOUND,
    InternalStatus.USER_ALREADY_EXISTS: StatusMessage.USERNAME_TAKEN,
    InternalStatus.WRONG_PASSWORD: StatusMessage.WRONG_PASSWORD,
    InternalStatus.INVALID_TOKEN: StatusMessage.INVALID_TOKEN,
    InternalStatus.TOKEN_EXPIRED: StatusMessage.TOKEN_EXPIRED,
    InternalStatus.DB_CONNECTION_FAILED: StatusMessage.SERVICE_UNAVAILABLE,
}


def get_http_status(
    internal_status: InternalStatus, default: int = status.HTTP_400_BAD_REQUEST
) -> int:
    return STATUS_CODE_MAP.get(internal_status, default)


def get_status_message(
    internal_status: InternalStatus, custom_message: str | None = None
) -> str:
    """Get user-facing message from internal status."""
    if custom_message:
        return custom_message
    return STATUS_MESSAGE_MAP.get(internal_status, StatusMessage.INTERNAL_ERROR)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Dependency to extract and validate user from JWT token."""
    result = auth_service.get_user_from_token(token)

    if result.is_failure:
        raise HTTPException(
            status_code=get_http_status(result.status, status.HTTP_401_UNAUTHORIZED),
            detail=get_status_message(result.status, result.message),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return result.data  # type: ignore


def get_auth_service() -> AuthenticationService:
    """Dependency to get AuthenticationService instance."""
    return auth_service


def get_user_service() -> UserService:
    """Dependency to get UserService instance."""
    return user_service
