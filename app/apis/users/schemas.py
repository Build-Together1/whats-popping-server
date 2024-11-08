import random
from datetime import date
from typing import List

from pydantic import BaseModel, EmailStr, UUID4, model_validator

from app.apis.events.schemas import EventPublic, CommentPublic


class UserBase(BaseModel):
    name: str
    email_address: EmailStr
    date_of_birth: date
    password: str
    confirm_password: str
    username: str
    profile_header_path: str
    profile_pic_path: str
    location: str
    website: str


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    name: str | None = None
    profile_header_path: str | None = None
    profile_pic_path: str | None = None
    location: str | None = None
    website: str | None = None

class UserPublic(BaseModel):
    name: str
    email_address: EmailStr
    date_of_birth: date
    username: str
    profile_header_path: str
    profile_pic_path: str
    location: str
    website: str
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True



class ReadUser(BaseModel):
    id: UUID4

class DeleteUser(BaseModel):
    id: UUID4

class UpdateUser(BaseModel):
    id: UUID4








