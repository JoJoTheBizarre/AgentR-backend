from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from service import verify_credentials, InternalStatus, create_jwt_token, register_user
from .status import StatusDetail
from .dto import UserIn

user_router = APIRouter(prefix="/user")


@user_router.post("/token")
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
    

@user_router.post("/register", status_code=201)
async def register(user: UserIn):
    register_status = register_user(**user.model_dump())

    if register_status == InternalStatus.SUCCESS:
        return {"status": StatusDetail.SUCCESS}
    
    if register_status == InternalStatus.USER_ALREADY_EXISTS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=InternalStatus.USER_ALREADY_EXISTS
        )



