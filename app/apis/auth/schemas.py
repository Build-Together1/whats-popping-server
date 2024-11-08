from typing import List, Dict, Any

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    email_address: EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str
    email: EmailStr


class UserLogin(BaseModel):
    id: str
    email_address: EmailStr
    password: str


class AccountLogin(BaseModel):
    email_address: EmailStr
    password: str


class VerifyEmail(BaseModel):
    otp: str
    email_address: EmailStr


class PasswordResetIn(User):
    pass


class PasswordResetConfirmation(PasswordResetIn):
    reset_code: str
    password: str
    confirm_password: str


class ChangePassword(BaseModel):
    email_address: EmailStr
    old_password: str
    new_password: str
    confirm_password: str


class EnableUser(User):
    pass


class DisableUser(User):
    pass


class GenerateOtp(User):
    pass


class DeleteUser(User):
    pass


class RefreshToken(BaseModel):
    email: EmailStr
    token: str


class CreateToken(BaseModel):
    user_id: str
    email_address: EmailStr
    access_token: str
    refresh_token: str
    access_expires_in_minutes: int
    refresh_expires_in_minutes: int
