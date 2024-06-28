from datetime import datetime, timedelta
from typing import List, Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from app.apis.auth.utils import generate_otp, Password
# from app.apis.users.corporate.models import CorporateOTPCodes
from app.database.session import db_dependency
from .models import CorporateAccount
from app.apis.users.schemas import (
    CorporateAccountCreate,
    CorporateAccountResponse,
    DeleteAccount, AccountRead, CorporateAccountOut
)
# from app.apis.auth.corporate.services import get_current_active_corporate_account
from app.apis.auth.services import get_current_active_corporate_account
from app.apis.auth.schemas import UserLogin
from ...auth.models import OTPCodes

corporate_router = APIRouter(tags=["CORPORATE ACCOUNT"])

auth_dependency = Annotated[UserLogin, Depends(get_current_active_corporate_account)]


@corporate_router.post(
    "/create-corporate-account", status_code=status.HTTP_201_CREATED, response_model=CorporateAccountOut
)
async def create_corporate_account(req: CorporateAccountCreate, db: db_dependency):
    existing_account = db.query(CorporateAccount).filter(CorporateAccount.email_address == req.email_address)
    if existing_account.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User already exist")

    if len(req.password) < 8:
        msg = "Password must be greater than 8 characters."
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=msg)
    elif not any(char.isdigit() for char in req.password):
        msg = "Password must contain at least one numeric digit."
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=msg)
    elif not any(char.isupper() for char in req.password):
        msg = "Password must contain at least one Upper letter."
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=msg)
    elif req.password != req.confirm_password:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Passwords do not match")

    req.password = Password.hash_password(req.password)
    req.confirm_password = Password.hash_password(req.confirm_password)

    user_dict = req.model_dump()
    account = CorporateAccount(
        **user_dict,
        is_active=False,
        is_verified=False
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    generated_otp = generate_otp()
    created_at = datetime.utcnow()
    expires_in = created_at + timedelta(minutes=3)

    otp_code = OTPCodes()
    otp_code.corporate_id = account.id
    otp_code.otp_code = generated_otp
    otp_code.expires_in = expires_in

    db.add(otp_code)
    db.commit()
    db.refresh(otp_code)

    return account

    # return {
    #     "message": f"Your account has been created successfully. "
    #                f"Verify your account by inputting {generated_otp}",
    # }


@corporate_router.post(
    "/corporate-account/{id}", status_code=status.HTTP_200_OK, response_model=CorporateAccountOut
)
async def get_corporate_account(req: AccountRead, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    account = db.query(CorporateAccount).filter(CorporateAccount.id == req.id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    return account


@corporate_router.get("/corporate-accounts", response_model=List[CorporateAccountOut])
async def get_all_corporate_accounts(db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    accounts = db.query(CorporateAccount).all()
    return accounts


@corporate_router.delete(
    "/corporate-account/{id}", status_code=status.HTTP_200_OK
)
async def delete_corporate_account(req: DeleteAccount, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    user_delete = db.query(CorporateAccount).filter(CorporateAccount.id == req.id)
    if not user_delete.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    user_delete.delete(synchronize_session=False)
    db.commit()

    return {"message": "Deleted successfully"}


@corporate_router.delete("/corporate-accounts", status_code=status.HTTP_200_OK)
async def delete_all_corporate_accounts(db: db_dependency):
    corporate_account_delete = db.query(CorporateAccount).all()

    for organizer in corporate_account_delete:
        db.delete(organizer)
    db.commit()
    return {"message": "Users deleted successfully"}
