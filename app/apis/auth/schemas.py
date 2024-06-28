from typing import List, Dict, Any

from pydantic import BaseModel, EmailStr


class Account(BaseModel):
    email_address: EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    account_id: str
    email: EmailStr
    role: str


class UserLogin(BaseModel):
    id: str
    email_address: EmailStr
    password: str


class EmailSchema(BaseModel):
    email: List[EmailStr]
    # body: Dict[str, Any]


class VerifyEmail(BaseModel):
    otp: str
    email_address: EmailStr


class PasswordResetIn(Account):
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


class EnableAccount(Account):
    pass


class DisableAccount(Account):
    pass


class GenerateOtp(Account):
    pass


class DeleteAccount(Account):
    pass


class RefreshToken(BaseModel):
    email: EmailStr
    token: str


class CreateToken(BaseModel):
    account_id: str
    email_address: EmailStr
    access_token: str
    refresh_token: str
    access_expires_in_minutes: int
    refresh_expires_in_minutes: int
