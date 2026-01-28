from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.services import (
    verify_credentials,
    create_jwt_token,
    register_user,
    InternalStatus,
)
from src.routes.status import StatusDetail
from src.schemas.models import UserCreate, TokenResponse, RegistrationResponse

user_router = APIRouter(prefix="/user")


@user_router.post(
    "/token", response_model=TokenResponse, response_model_exclude_none=True
)
async def create_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    auth_status = verify_credentials(form_data.username, form_data.password)
    if auth_status == InternalStatus.SUCCESS:
        access_token = create_jwt_token(form_data.username)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=StatusDetail.INVALID_CREDENTIALS,
        )


@user_router.post(
    "/register",
    status_code=201,
    response_model=RegistrationResponse,
    response_model_exclude_none=True,
)
async def register(user: UserCreate):
    register_status = register_user(**user.model_dump())

    if register_status == InternalStatus.SUCCESS:
        return RegistrationResponse(status=StatusDetail.SUCCESS)

    if register_status == InternalStatus.USER_ALREADY_EXISTS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=InternalStatus.USER_ALREADY_EXISTS,
        )
