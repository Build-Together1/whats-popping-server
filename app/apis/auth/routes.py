from typing import Annotated

from fastapi import APIRouter, status, Depends, Response, Request, HTTPException, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.apis.auth.schemas import (
    Token
)
from app.config import settings
from app.apis.auth.schemas import UserLogin
from app.database.session import db_dependency
from .services import (
    authenticate_individual_account,
    get_current_active_individual_account,
    authenticate_corporate_account,
    get_current_active_corporate_account,
    individual_refresh_access_token,
    corporate_refresh_access_token, logout_account, login_account
)
from ...exceptions.base_exception import CredentialsException

auth_router = APIRouter(tags=["ACCOUNT AUTHENTICATION & AUTHORIZATION"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)

individual_auth_dependency = Annotated[UserLogin, Depends(get_current_active_individual_account)]
corporate_auth_dependency = Annotated[UserLogin, Depends(get_current_active_corporate_account)]


@auth_router.post("/auth/login")
async def login_for_access_token(
        response: Response,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency
):
    individual_account = authenticate_individual_account(
        db=db,
        email=form_data.username,
        password=form_data.password
    )
    if individual_account:
        return await login_account(response, account=individual_account, role="individual")

    corporate_account = authenticate_corporate_account(
        db=db,
        email=form_data.username,
        password=form_data.password
    )
    if corporate_account:
        return await login_account(response, account=corporate_account, role="corporate")

    raise CredentialsException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"}
    )


@auth_router.post("/individual/token/refresh", response_model=Token)
async def refresh_access_token_individual(response: Response, db: db_dependency, refresh_token: str = Cookie(None)):
    return await individual_refresh_access_token(response, db, refresh_token)


@auth_router.post("/corporate/token/refresh", response_model=Token)
async def refresh_access_token_corporate(response: Response, db: db_dependency, refresh_token: str = Cookie(None)):
    return await corporate_refresh_access_token(response, db, refresh_token)


@auth_router.delete("/individual-account-logout")
async def individual_account_logout(
        response: Response,
        request: Request,
        db: db_dependency,
        current_user: individual_auth_dependency,
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return await logout_account(response, request, db)


@auth_router.get("/corporate-account-logout")
async def corporate_account_logout(
        response: Response,
        request: Request,
        db: db_dependency,
        current_user: corporate_auth_dependency,
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return await logout_account(response, request, db)
