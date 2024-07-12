from datetime import datetime, timedelta
from typing import Annotated
from typing import List

from fastapi import APIRouter, Depends
from fastapi import BackgroundTasks, HTTPException, status

from app.apis.auth.schemas import UserLogin
from app.apis.auth.services import get_current_active_individual_account
from app.apis.auth.utils import generate_otp, Password, password_checker
from app.config import env
from app.database.session import db_dependency
from . import crud
from .models import IndividualAccount
from ..schemas import (
    IndividualAccountCreate,
    DeleteAccount, AccountRead, IndividualAccountOut
)
from ...auth.email import send_email_background
from ...auth.models import OTPCodes

individual_router = APIRouter(tags=["INDIVIDUAL ACCOUNT"])

auth_dependency = Annotated[UserLogin, Depends(get_current_active_individual_account)]


@individual_router.post(
    "/create-individual-account", status_code=status.HTTP_201_CREATED
)
async def create_individual_account(
        req: IndividualAccountCreate,
        db: db_dependency,
        background_tasks: BackgroundTasks
):
    existing_account = await crud.get_account_by_email(req, db)
    if existing_account:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This account already exists")

    await password_checker(req.password, req.confirm_password)

    req.password = Password.hash_password(req.password)
    req.confirm_password = Password.hash_password(req.confirm_password)

    user_dict = req.model_dump()
    # account = crud.save_account_to_db(user_dict, db)
    account = IndividualAccount(
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
    otp_code.individual_id = account.id
    otp_code.otp_code = generated_otp
    otp_code.expires_in = expires_in

    db.add(otp_code)
    db.commit()
    db.refresh(otp_code)

    template = env.get_template("welcome_email.html")
    html_body = template.render(username=account.first_name, otp=generated_otp)

    send_email_background(background_tasks, "What's Popping Account Verification", account.email_address, html_body)

    return [
        {"message": "User registered successfully. Confirmation email will be sent shortly."},
        account
    ]


@individual_router.post(
    "/individual-account/{id}", status_code=status.HTTP_200_OK, response_model=IndividualAccountOut
)
async def get_individual_account(req: AccountRead, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    account = db.query(IndividualAccount).filter(IndividualAccount.id == req.id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    return account


@individual_router.get(
    "/individual-accounts", status_code=status.HTTP_200_OK, response_model=List[IndividualAccountOut]
)
async def get_all_individual_accounts(db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    users = db.query(IndividualAccount).all()

    return users


@individual_router.delete(
    "/individual-account/{id}", status_code=status.HTTP_200_OK
)
async def delete_individual_account(req: DeleteAccount, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    delete_account = db.query(IndividualAccount).filter(IndividualAccount.id == req.id)
    if not delete_account.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    delete_account.delete(synchronize_session=False)
    db.commit()

    return {"message": "Deleted successfully"}


@individual_router.delete(
    "/delete-individual-accounts", status_code=status.HTTP_200_OK
)
async def delete_individual_accounts(db: db_dependency):
    accounts_delete = db.query(IndividualAccount).all()

    for user in accounts_delete:
        db.delete(user)
    db.commit()

    return {"message": "Users deleted successfully"}
