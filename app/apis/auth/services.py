from datetime import timedelta, datetime
from datetime import timezone
from typing import Annotated

from fastapi import Depends, Request, Response, Cookie
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt, ExpiredSignatureError

from app.config import env
from app.config import settings
from app.database.models import User, PasswordReset
from app.database.session import db_dependency
from . import crud
from .email import send_email_background
from .schemas import TokenData, Token, RefreshToken
from .utils import Password, generate_otp, password_checker
from ...exceptions.base_exception import CredentialsException

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


credentials_exception = CredentialsException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
)


class UserAccount:

    @staticmethod
    def authenticate_user_account(db, email: str, password: str):
        # Retrieve user by email
        user = crud.get_user_by_email(db, email)
        if (
                user and
                Password.verify_password(plain_password=password, hashed_password=user.password)
        ):
            return user
        return None


    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str):
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        email: str = payload.get("sub")
        if email is None or user_id is None:
            raise credentials_exception
        return TokenData(user_id=user_id, email=email)

    @staticmethod
    async def user_refresh_access_token(response: Response, db: db_dependency, refresh_token: str = Cookie(None)):
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")

        try:
            token_data = UserAccount.decode_token(token=refresh_token)
            # Check if account exists
            user = crud.get_user_by_id(db, user_id=token_data.user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

            # Generate new access token
            access_token = UserAccount.create_access_token(
                data={
                    "id": str(user.id),
                    "sub": user.email_address
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

    @staticmethod
    async def login_account(response: Response, user):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = UserAccount.create_access_token(
            data={
                "id": str(user.id),
                "sub": user.email_address,
            },
            expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_token = UserAccount.create_refresh_token(
            data={
                "id": str(user.id),
                "sub": user.email_address,
            },
            expires_delta=refresh_token_expires
        )

        # tokens stored as HTTP-only cookies
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    @staticmethod
    async def logout_user(response, request, db):
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        if access_token:
            crud.save_blacklisted_access_token_to_db(db, access_token)
            response.delete_cookie(key="access_token")
        if refresh_token:
            crud.save_blacklisted_refresh_token_to_db(db, refresh_token)
            response.delete_cookie(key="refresh_token")

        return {"msg": "Logged out successfully"}


    @staticmethod
    def get_current_user(
            request: Request,
            db: db_dependency,
            access_token: str = Depends(oauth2_scheme)
    ):
        token = request.cookies.get("access_token")
        if token != access_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        blacklisted_token = crud.get_blacklisted_token(db, token)
        if blacklisted_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You are logged out. Log in to continue.")

        try:
            token_data = UserAccount.decode_token(token=token)
        except ExpiredSignatureError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired token. Login to obtain a new token."
            )
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

        user = crud.get_user_by_id(db, user_id=token_data.user_id)
        if user:
            return user

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    @staticmethod
    async def get_current_active_user(
            current_user: Annotated[User, Depends(get_current_user)]
    ):
        if not current_user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive User")
        return current_user

    @staticmethod
    async def verify_email(req, db, background_tasks):
        user = crud.get_user_by_email(db, req.email_address)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        otp = crud.get_otp_code(req, db)
        if not otp:
            raise HTTPException(status_code=404, detail="invalid OTP")

        if user and otp:
            current_time = datetime.now(timezone.utc)
            if otp.expires_in < current_time:
                raise HTTPException(status_code=404, detail="expired OTP")

        await crud.save_user_to_db(user, db)

        template = env.get_template("account_activation.html")
        html_body = template.render(username=user.name)

        send_email_background(background_tasks, "Account Verified", user.email_address, html_body)

        return {"msg": "Email verified"}

    @staticmethod
    async def otp_for_email_verification(req, db, background_tasks):
        user = crud.get_user_by_email(db, req.email_address)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        generated_otp = generate_otp()
        created_at = datetime.now(timezone.utc)
        expires_in = created_at + timedelta(minutes=2)

        await crud.save_otp_to_db(generated_otp, expires_in, db)

        template = env.get_template("welcome_email.html")
        html_body = template.render(username=user.name, otp=generated_otp)

        send_email_background(background_tasks, "What's Popping Account Verification", user.email_address, html_body)

        return {
            "message": f"Your otp has been generated successfully. "
                       f"Verify your account by inputting {generated_otp}"
        }

    @staticmethod
    async def change_user_password(req, db, current_user, background_tasks):
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

        user = crud.get_user_by_email(req, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        check_password = Password.verify_password(req.old_password, current_user.password)
        if not check_password:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="Invalid password. Check old password")

        await password_checker(req.new_password, req.confirm_password)

        password = Password.hash_password(req.new_password)
        confirm_password = Password.hash_password(req.confirm_password)

        await crud.save_password_to_db(user, password, confirm_password, db)

        template = env.get_template("password_change.html")
        html_body = template.render(username=user.name)

        send_email_background(background_tasks, "A password change on your What's Popping account", account.email_address, html_body)

        return {"msg": "Password changed successfully"}

    @staticmethod
    async def user_reset_otp(req, db, background_tasks):
        user = crud.get_user_by_email(req, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        generated_otp = generate_otp()
        created_at = datetime.now(timezone.utc)
        expires_in = created_at + timedelta(minutes=2)

        reset_code = PasswordReset()
        reset_code.reset_code = generated_otp
        reset_code.expires_in = expires_in

        await crud.save_reset_code_to_db(reset_code, db)

        template = env.get_template("password_reset.html")
        html_body = template.render(username=user.name, otp=generated_otp)

        send_email_background(background_tasks, "Reset Password", user.email_address, html_body)

        return {
            "message": f"Your otp has been generated successfully. "
                       f"reset your password by inputting {generated_otp}"
        }

    @staticmethod
    async def user_password_reset(req, db, background_tasks):
        user = crud.get_user_by_email(req, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        reset_code = crud.get_reset_code(req, db)
        if not reset_code:
            raise HTTPException(status_code=404, detail="invalid OTP")

        if user and reset_code:
            current_time = datetime.now(timezone.utc)
            if reset_code.expires_in < current_time:
                raise HTTPException(status_code=404, detail="expired OTP")

        await password_checker(req.password, req.confirm_password)

        password = Password.hash_password(req.password)
        confirm_password = Password.hash_password(req.confirm_password)

        await crud.save_password_to_db(user, password, confirm_password, db)
        template = env.get_template("password_change.html")
        html_body = template.render(username=user.name)

        send_email_background(background_tasks, "A password change on your What's Popping account",
                             user.email_address, html_body)

        return {"msg": "Password reset successful"}

    @staticmethod
    async def disable_user(req, db, current_user):
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
        account = crud.get_user_by_email(req, db)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await crud.save_disabled_user_to_db(account, db)

        return {"message": "User disabled successfully"}

    @staticmethod
    async def enable_user(req, db):
        account = crud.get_user_by_email(req, db)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await crud.save_enabled_user_to_db(account, db)

        return {"message": "User enabled successfully"}
