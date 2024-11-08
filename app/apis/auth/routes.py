from typing import Annotated

from fastapi import APIRouter, status, Depends, BackgroundTasks
from fastapi import Response, Request, HTTPException, Cookie

from app.config import settings
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.apis.auth.schemas import UserLogin, Token, AccountLogin
from app.apis.auth.schemas import (
    VerifyEmail,
    GenerateOtp,
    PasswordResetConfirmation,
    ChangePassword, PasswordResetIn, DisableUser, EnableUser,
)
from app.database.session import db_dependency
from .services import UserAccount
from ...exceptions.base_exception import CredentialsException

auth_router = APIRouter(tags=["USER AUTHENTICATION & AUTHORIZATION"])

auth_dependency = Annotated[UserLogin, Depends(UserAccount.get_current_active_user)]

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)


@auth_router.post("/login")
async def login_for_access_token(
        response: Response,
        # form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_login: AccountLogin,
        db: db_dependency
):
    user = UserAccount.authenticate_user_account(
        db=db,
        email=user_login.email_address,
        password=user_login.password
    )

    # user = UserAccount.authenticate_user_account(
    #     db=db,
    #     email=form_data.username,
    #     password=form_data.password
    # )
    if user:
        return await UserAccount.login_account(response, user=user)

    raise CredentialsException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"}
    )


@auth_router.post("/token/refresh", response_model=Token)
async def refresh_access_token(response: Response, db: db_dependency, refresh_token: str = Cookie(None)):
    return await UserAccount.user_refresh_access_token(response, db, refresh_token)


@auth_router.post("/verify_email")
async def verify_email(
        req: VerifyEmail, db: db_dependency, background_tasks: BackgroundTasks
):
    return await UserAccount.verify_email(req, db, background_tasks)


@auth_router.post("/generate_otp")
async def otp_for_email_verification(
        req: GenerateOtp, db: db_dependency,  background_tasks: BackgroundTasks
):
    return await  UserAccount.otp_for_email_verification(req, db, background_tasks)


@auth_router.patch("/change_password")
async def change_password(
        req: ChangePassword, db: db_dependency, current_user: auth_dependency,  background_tasks: BackgroundTasks
):
    return await UserAccount.change_user_password(req, db, current_user, background_tasks)


@auth_router.post("/reset_password")
async def user_password_reset(
        req: PasswordResetIn, db: db_dependency, background_tasks: BackgroundTasks
):
    return await UserAccount.user_reset_otp(req, db, background_tasks)


@auth_router.patch("/confirm_password_reset")
async def user_confirm_password_reset(
        req: PasswordResetConfirmation, db: db_dependency, background_tasks: BackgroundTasks
):
    return await UserAccount.user_password_reset(req, db, background_tasks)

@auth_router.post("/enable_user", status_code=status.HTTP_200_OK)
async def enable_user(req: EnableUser, db: db_dependency):
    return await UserAccount.enable_user(req, db)

@auth_router.post("/disable_user", status_code=status.HTTP_200_OK)
async def disable_user(
        req: DisableUser, db: db_dependency, current_user: auth_dependency
):
    return await UserAccount.disable_user(req, db, current_user)

@auth_router.delete("/user_logout")
async def user_logout(
        response: Response,
        request: Request,
        db: db_dependency,
        current_user: auth_dependency,
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return await UserAccount.logout_user(response, request, db)

