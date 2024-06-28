from typing import Annotated

from fastapi import APIRouter, status, Depends

from app.apis.auth.schemas import (
    VerifyEmail,
    GenerateOtp,
    PasswordResetConfirmation,
    ChangePassword, DisableAccount,
    PasswordResetIn, EnableAccount, UserLogin
)
from app.database.session import db_dependency
from .services import CorporateUserAccount
from ..services import (
    get_current_active_corporate_account
)

corporate_auth_router = APIRouter(tags=["CORPORATE ACCOUNT AUTHENTICATION & AUTHORIZATION"])

auth_dependency = Annotated[UserLogin, Depends(get_current_active_corporate_account)]


@corporate_auth_router.post("/corporate-account-verify-email")
async def corporate_account_verify_email(req: VerifyEmail, db: db_dependency):
    return await CorporateUserAccount.verify_email(req, db)


@corporate_auth_router.post("/corporate-account-generate-otp")
async def corporate_account_otp_for_email_verification(req: GenerateOtp, db: db_dependency):
    return await CorporateUserAccount.otp_for_email_verification(req, db)


@corporate_auth_router.patch("/corporate-account-change_password")
async def corporate_account_change_password(req: ChangePassword, db: db_dependency, current_user: auth_dependency):
    return await CorporateUserAccount.change_account_password(req, db, current_user)


@corporate_auth_router.post("/corporate-account-reset_password")
async def corporate_account_reset_password(req: PasswordResetIn, db: db_dependency):
    return await CorporateUserAccount.account_reset_otp(req, db)


@corporate_auth_router.patch("/corporate-account-confirm-password-reset")
async def corporate_account_confirm_password_reset(req: PasswordResetConfirmation, db: db_dependency):
    return await CorporateUserAccount.account_password_reset(req, db)


@corporate_auth_router.post("/disable-corporate-account", status_code=status.HTTP_200_OK)
async def disable_corporate_account(req: DisableAccount, db: db_dependency, current_user: auth_dependency):
    return await CorporateUserAccount.disable_account(req, db, current_user)


@corporate_auth_router.post("/enable-corporate-account", status_code=status.HTTP_200_OK)
async def enable_corporate_account(req: EnableAccount, db: db_dependency):
    return await CorporateUserAccount.enable_account(req, db)
