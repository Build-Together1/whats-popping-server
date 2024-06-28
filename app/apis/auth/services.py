from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status, Request, Response, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt, ExpiredSignatureError

from app.apis.auth.utils import Password
from app.apis.users.corporate.models import CorporateAccount
from app.apis.users.individual.models import IndividualAccount
from app.config import settings
from app.database.session import db_dependency
from . import crud
from .schemas import TokenData, Token, RefreshToken
from ...exceptions.base_exception import CredentialsException

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

credentials_exception = CredentialsException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
)


def authenticate_individual_account(db, email: str, password: str):
    # Retrieve user by email
    individual_account = crud.get_individual_account_by_email(db, email)
    if (
            individual_account and
            Password.verify_password(plain_password=password, hashed_password=individual_account.password)
    ):
        return individual_account
    return None


def authenticate_corporate_account(db, email: str, password: str):
    # Retrieve organizer by email
    corporate_account = crud.get_corporate_account_by_email(db, email)
    if (
            corporate_account and
            Password.verify_password(plain_password=password, hashed_password=corporate_account.password)
    ):
        return corporate_account
    return None


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    account_id: str = payload.get("id")
    email: str = payload.get("sub")
    role: str = payload.get("role")
    if email is None or account_id is None:
        raise credentials_exception
    return TokenData(account_id=account_id, email=email, role=role)


async def individual_refresh_access_token(response: Response, db: db_dependency, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")

    try:
        token_data = decode_token(token=refresh_token)
        # Check if account exists
        individual_account = crud.get_individual_account_by_id(db, account_id=token_data.account_id)
        if not individual_account:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        # Generate new access token
        access_token = create_access_token(
            data={
                "id": str(individual_account.id),
                "sub": individual_account.email_address,
                "role": "individual"
            },
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        # Set the new access token as an HTTP-only cookie
        response.set_cookie(key="access_token", value=access_token, httponly=True)

        return RefreshToken(
            access_token=access_token,
            token_type="bearer"
        )

    except ExpiredSignatureError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


async def corporate_refresh_access_token(response: Response, db: db_dependency, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")

    try:
        token_data = decode_token(token=refresh_token)
        # Check if account exists
        corporate_account = crud.get_corporate_account_by_id(db, account_id=token_data.account_id)
        if not corporate_account:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        # Generate new access token
        access_token = create_access_token(
            data={
                "id": str(corporate_account.id),
                "sub": corporate_account.email_address,
                "role": "corporate"
            },
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        # Set the new access token as an HTTP-only cookie
        response.set_cookie(key="access_token", value=access_token, httponly=True)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    except ExpiredSignatureError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


async def login_account(response: Response, account, role: str):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "id": str(account.id),
            "sub": account.email_address,
            "role": role
        },
        expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_access_token(
        data={
            "id": str(account.id),
            "sub": account.email_address,
            "role": role
        },
        expires_delta=refresh_token_expires
    )

    # Set the tokens as HTTP-only cookies
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


async def logout_account(response, request, db):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if access_token:
        crud.save_blacklisted_access_token_to_db(db, access_token)
        response.delete_cookie(key="access_token")
    if refresh_token:
        crud.save_blacklisted_refresh_token_to_db(db, refresh_token)
        response.delete_cookie(key="refresh_token")

    return {"msg": "Logged out successfully"}


def get_current_individual_account(
        request: Request,
        db: db_dependency,
        access_token: str = Depends(oauth2_scheme)
):
    token = request.cookies.get("access_token")
    if token != access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    blacklisted_token = crud.get_blacklisted_token(db, token)
    if blacklisted_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are logged out. Log in to continue.")

    try:
        token_data = decode_token(token=token)
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token. Login to obtain a new token."
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    if token_data.role != "individual":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    individual_account = crud.get_individual_account_by_id(db, account_id=token_data.account_id)
    if individual_account:
        return individual_account

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


def get_current_corporate_account(
        request: Request,
        db: db_dependency,
        access_token: str = Depends(oauth2_scheme)
):
    token = request.cookies.get("access_token")
    if token != access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    blacklisted_token = crud.get_blacklisted_token(db, token)
    if blacklisted_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are logged out. Log in to continue.")

    try:
        token_data = decode_token(token=token)
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token. Login to obtain a new token."
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    if token_data.role != "corporate":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    corporate_account = crud.get_corporate_account_by_id(db, account_id=token_data.account_id)
    if corporate_account:
        return corporate_account

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


async def get_current_active_individual_account(
        current_user: Annotated[IndividualAccount, Depends(get_current_individual_account)]
):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive User")
    return current_user


async def get_current_active_corporate_account(
        current_user: Annotated[CorporateAccount, Depends(get_current_corporate_account)]
):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive User")
    return current_user
