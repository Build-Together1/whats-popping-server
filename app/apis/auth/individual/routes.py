from typing import Annotated

from fastapi import APIRouter, status, Depends

from app.apis.auth.schemas import UserLogin
from app.apis.auth.schemas import (
    VerifyEmail,
    GenerateOtp,
    PasswordResetConfirmation,
    ChangePassword, DisableAccount,
    PasswordResetIn, EnableAccount
)
from app.database.session import db_dependency
from .services import IndividualUserAccount
from ..services import (
    get_current_active_individual_account,
)

individual_auth_router = APIRouter(tags=["INDIVIDUAL ACCOUNT AUTHENTICATION & AUTHORIZATION"])

auth_dependency = Annotated[UserLogin, Depends(get_current_active_individual_account)]


@individual_auth_router.post("/individual-account-verify-email")
async def individual_account_verify_email(req: VerifyEmail, db: db_dependency):
    return await IndividualUserAccount.verify_email(req, db)


@individual_auth_router.post("/individual-account-generate-otp")
async def individual_account_otp_for_email_verification(req: GenerateOtp, db: db_dependency):
    return await IndividualUserAccount.otp_for_email_verification(req, db)


@individual_auth_router.patch("/individual-account-change_password")
async def individual_account_change_password(req: ChangePassword, db: db_dependency, current_user: auth_dependency):
    return await IndividualUserAccount.change_account_password(req, db, current_user)


@individual_auth_router.post("/individual-account-reset_password")
async def individual_account_reset_password(req: PasswordResetIn, db: db_dependency):
    return await IndividualUserAccount.account_reset_otp(req, db)


@individual_auth_router.patch("/individual-account-confirm_password_reset")
async def individual_account_confirm_password_reset(req: PasswordResetConfirmation, db: db_dependency):
    return await IndividualUserAccount.account_password_reset(req, db)


@individual_auth_router.post("/disable-individual-account", status_code=status.HTTP_200_OK)
async def disable_individual_account(req: DisableAccount, db: db_dependency, current_user: auth_dependency):
    return await IndividualUserAccount.disable_account(req, db, current_user)


@individual_auth_router.post("/enable-individual-account", status_code=status.HTTP_200_OK)
async def enable_individual_account(req: EnableAccount, db: db_dependency):
    return await IndividualUserAccount.enable_account(req, db)
