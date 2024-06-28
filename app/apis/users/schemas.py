from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Annotated


class AccountBase(BaseModel):
    first_name: str
    last_name: str
    email_address: EmailStr
    phone_number: str
    state: str
    country: str
    password: str
    confirm_password: str


class IndividualAccountCreate(AccountBase):
    pass


class CorporateAccountCreate(AccountBase):
    organization_name: str
    organization_description: str


class IndividualAccountResponse(IndividualAccountCreate):
    id: UUID4
    is_verified: bool

    class Config:
        from_attributes = True


class CorporateAccountResponse(CorporateAccountCreate):
    id: UUID4
    is_verified: bool

    class Config:
        from_attributes = True


class DeleteAccount(BaseModel):
    id: UUID4


class AccountRead(BaseModel):
    id: UUID4


class IndividualAccountOut(BaseModel):
    id: UUID4
    first_name: str
    last_name: str
    email_address: EmailStr
    phone_number: str
    state: str
    country: str
    is_active: bool
    is_verified: bool


class CorporateAccountOut(BaseModel):
    id: UUID4
    first_name: str
    last_name: str
    email_address: EmailStr
    phone_number: str
    state: str
    country: str
    organization_name: str
    organization_description: str
    is_active: bool
    is_verified: bool
