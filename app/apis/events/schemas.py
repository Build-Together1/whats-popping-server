from datetime import date, time

from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Annotated, List
from datetime import datetime

from app.database.models import Events, Comments


class EventBase(BaseModel):
    event_name: str
    event_description: str
    event_category: str
    event_image: str
    event_date: date
    event_time: time
    event_location: str

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    event_name: str | None = None
    event_description: str | None = None
    event_category: str | None = None
    event_image: str | None = None
    event_date: date | None = None
    event_time: time | None = None
    event_location: str | None = None

class ReadEvent(BaseModel):
    id: UUID4

class DeleteEvent(BaseModel):
    id: UUID4

class UpdateEvent(BaseModel):
    id: UUID4

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentUpdate(CommentBase):
    content: str | None = None

class CommentPublic(BaseModel):
    content: str

    class Config:
        from_attributes = True


# LIKE SCHEMAS

class LikeCreate(BaseModel):
    event_id: UUID4

# Schema for displaying like details
class LikeResponse(BaseModel):
    user_id: UUID4
    event_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

# Schema for displaying an event with like count
class EventWithLikes(BaseModel):
    like_count: int

    class Config:
        from_attributes = True


class EventPublic(BaseModel):
    event_name: str
    event_description: str
    event_category: str
    event_image: str
    event_date: date
    event_time: time
    event_location: str
    comments: List[CommentPublic] = []
    likes: EventWithLikes

    class Config:
        from_attributes = True


class UserEventsPublic(EventBase):
    events: List[EventPublic]

    class Config:
        from_attributes = True


class UserWithEvents(BaseModel):
    name: str
    username: str
    profile_header_path: str
    profile_pic_path: str
    location: str
    website: str

    events: List[EventPublic] = []

    class Config:
        from_attributes = True