from datetime import datetime, timedelta, timezone
from random import randint
from typing import Annotated
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import BackgroundTasks, HTTPException, status

from app.apis.auth.email import send_email_background
from app.apis.auth.schemas import UserLogin
from app.apis.auth.services import UserAccount
from app.apis.auth.utils import generate_otp, Password, password_checker
from app.apis.users.schemas import (
    UserCreate, DeleteUser, ReadUser, UserPublic, UserUpdate, UpdateUser
)
from app.config import env
from app.database.models import User, OTPCodes
from app.database.session import db_dependency
from . import crud

user_router = APIRouter(tags=["USERS ACCOUNT"])

auth_dependency = Annotated[UserLogin, Depends(UserAccount.get_current_active_user)]


@user_router.post(
    "/users/", status_code=status.HTTP_201_CREATED
)
async def create_user(
        req: UserCreate,
        db: db_dependency,
        background_tasks: BackgroundTasks
):
    existing_email = await crud.get_user_by_email(req, db)
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This email already exists")

    existing_username = await crud.get_user_by_username(req, db)
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This username is taken")

    if not req.username:
        req.username = req.name+ str(randint(100, 9999))

    # if datetime.now - req.date_of_birth < 18:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You must be above 18.")

    await password_checker(req.password, req.confirm_password)

    req.password = Password.hash_password(req.password)
    req.confirm_password = Password.hash_password(req.confirm_password)

    user_dict = req.model_dump()
    # account = crud.save_account_to_db(user_dict, db)
    user = User(
        **user_dict,
        is_active=False,
        is_verified=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    generated_otp = generate_otp()
    created_at = datetime.now(timezone.utc)
    expires_in = created_at + timedelta(minutes=3)

    otp_code = OTPCodes()
    otp_code.userid = user.id
    otp_code.otp_code = generated_otp
    otp_code.expires_in = expires_in

    db.add(otp_code)
    db.commit()
    db.refresh(otp_code)

    template = env.get_template("welcome_email.html")
    html_body = template.render(username=user.name, otp=generated_otp)

    send_email_background(background_tasks, "What's Popping Account Verification", user.email_address, html_body)

    return [
        {"message": "User registered successfully. Confirmation email will be sent shortly."},
        user
    ]


@user_router.post(
    "/users/{id}", status_code=status.HTTP_200_OK, response_model=UserPublic
)
async def read_user(user_id: ReadUser, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    user = db.query(User).filter(User.id == user_id.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    return user


#
# @user_router.post(
#     "/users/events/{id}", status_code=status.HTTP_200_OK, response_model=UserWithEvents
# )
# async def read_user_with_events(user_id: ReadUser, db: db_dependency, current_user: auth_dependency):
#     if not current_user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
#     user = db.query(User).filter(User.id == user_id.id).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
#
#     return user
#
#
# @user_router.get(
#     "/users/events", status_code=status.HTTP_200_OK, response_model=List[UserWithEvents]
# )
# async def get_all_users_with_events(db: db_dependency, current_user: auth_dependency):
#     if not current_user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
#     users = db.query(User).all()
#
#     return users


@user_router.get(
    "/users/", status_code=status.HTTP_200_OK, response_model=List[UserPublic]
)
async def get_all_users(db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    users = db.query(User).all()

    return users

# @user_router.patch(
#     "/users/", status_code=status.HTTP_200_OK, response_model=List[UserPublic]
# )
# async def get_all_users(db: db_dependency, current_user: auth_dependency):
#     if not current_user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
#     users = db.query(User).all()
#
#     return users


@user_router.patch("/users/{id}", response_model=UserPublic)
def update_user(user_id: UUID, req: UserUpdate, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Update fields in the existing user object with values from the request
    update_data = req.model_dump(exclude_unset=True)  # Only update fields provided in the request
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)  # Refresh to get the updated user data from the DB

    return user  # Return the updated user


@user_router.delete(
    "/users/{id}", status_code=status.HTTP_200_OK
)
async def delete_user(user_id: DeleteUser, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    user = db.query(User).filter(User.id == user_id.id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    user.delete(synchronize_session=False)
    db.commit()

    return {"message": "Deleted successfully"}


@user_router.delete(
    "/users", status_code=status.HTTP_200_OK
)
async def delete_users(db: db_dependency):
    users = db.query(User).all()

    for user in  users:
        db.delete(user)
    db.commit()

    return {"message": "Users deleted successfully"}