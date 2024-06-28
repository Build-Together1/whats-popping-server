import random
import string
from app.config import settings

from fastapi import HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Password:
    @staticmethod
    def hash_password(password):
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)


def generate_otp(length=settings.OTP_CODE_LENGTH):
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(length))


async def password_checker(password, confirm_password):
    if len(password) < settings.PASSWORD_LENGTH:
        msg = f"Password must be greater than {settings.PASSWORD_LENGTH} characters."
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=msg)
    elif not any(char.isdigit() for char in password):
        msg = "Password must contain at least one numeric digit."
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=msg)
    elif not any(char.isupper() for char in password):
        msg = "Password must contain at least one Upper letter."
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=msg)
    elif password != confirm_password:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Passwords do not match")


