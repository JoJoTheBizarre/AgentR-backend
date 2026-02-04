from fastapi import APIRouter, Depends, status, HTTPException

from src.routes.dependencies import (
    get_current_user,
    get_user_service,
    get_http_status,
    get_status_message,
)
from src.routes.schemas import (
    UserCreate,
    UserResponse,
    RegistrationResponse,
    PasswordChange,
    MessageResponse,
)
from src.routes.status_message import StatusMessage
from src.db.models import User
from src.services.user import UserService


user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with username and password.",
)
async def register(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    """
    Register a new user account.

    - **username**: Must be 3-50 characters, unique
    - **password**: Must be at least 8 characters
    """
    result = user_service.register_user(user.username, user.password)

    if result.is_success:
        return RegistrationResponse(
            status=StatusMessage.SUCCESS,
            message=result.message or "User registered successfully",
        )

    raise HTTPException(
        status_code=get_http_status(result.status, status.HTTP_400_BAD_REQUEST),
        detail=get_status_message(result.status, result.message),
    )


@user_router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Retrieve the profile of the currently authenticated user.",
)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get the profile of the currently authenticated user."""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        created_at=current_user.created_at.isoformat(),
        updated_at=current_user.updated_at.isoformat(),
    )


@user_router.put(
    "/me/password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change the password for the currently authenticated user.",
)
async def change_my_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Change the password for the currently authenticated user.

    Requires the current password for verification.
    """
    result = user_service.change_password(
        str(current_user.id), password_data.old_password, password_data.new_password
    )

    if result.is_success:
        return MessageResponse(
            status=StatusMessage.SUCCESS,
            message=result.message or "Password changed successfully",
        )

    raise HTTPException(
        status_code=get_http_status(result.status, status.HTTP_400_BAD_REQUEST),
        detail=get_status_message(result.status, result.message),
    )


@user_router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Delete current user account",
    description="Permanently delete the currently authenticated user's account.",
)
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Delete the currently authenticated user's account.

    This action is permanent and cannot be undone.
    """
    result = user_service.delete_user(str(current_user.id))

    if result.is_success:
        return MessageResponse(
            status=StatusMessage.SUCCESS,
            message=result.message or "Account deleted successfully",
        )

    raise HTTPException(
        status_code=get_http_status(result.status, status.HTTP_400_BAD_REQUEST),
        detail=get_status_message(result.status, result.message),
    )
