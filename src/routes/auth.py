from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.routes.dependencies import (
    get_auth_service,
    oauth2_scheme,
    get_http_status,
    get_status_message,
)
from src.routes.schemas import TokenResponse
from src.services.auth import AuthenticationService


auth_router = APIRouter(prefix="/auth", tags=["authentication"])


@auth_router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login and get access token",
    description="Authenticate with username and password to receive a JWT access token.",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """Authenticate user and return JWT access token."""
    result = auth_service.authenticate_user(form_data.username, form_data.password)

    if result.is_success:
        return TokenResponse(access_token=result.data, token_type="bearer")  # type: ignore

    raise HTTPException(
        status_code=get_http_status(result.status, status.HTTP_401_UNAUTHORIZED),
        detail=get_status_message(result.status, result.message),
    )


@auth_router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using your current token.",
)
def refresh_token(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    Refresh an expired or soon-to-expire token.

    Requires a valid or expired JWT token in the Authorization header.
    """
    result = auth_service.refresh_token(token)

    if result.is_success:
        return TokenResponse(access_token=result.data, token_type="bearer")  # type: ignore

    raise HTTPException(
        status_code=get_http_status(result.status, status.HTTP_401_UNAUTHORIZED),
        detail=get_status_message(result.status, result.message),
    )


@auth_router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
    summary="Verify token validity",
    description="Check if a token is valid without refreshing it.",
)
def verify_token(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """Verify if the provided token is valid."""
    result = auth_service.verify_jwt_token(token)

    if result.is_success:
        return {
            "valid": True,
            "username": result.data,
        }

    raise HTTPException(
        status_code=get_http_status(result.status, status.HTTP_401_UNAUTHORIZED),
        detail=get_status_message(result.status, result.message),
    )
