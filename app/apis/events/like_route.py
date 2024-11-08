from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi import status

from app.apis.auth.schemas import UserLogin
from app.apis.auth.services import UserAccount
from app.database.models import Events, Likes
from app.database.session import db_dependency
from .schemas import LikeResponse, EventWithLikes

like_router = APIRouter(tags=["LIKES"])

auth_dependency = Annotated[UserLogin, Depends(UserAccount.get_current_active_user)]




@like_router.post("/events/{event_id}/like", response_model=LikeResponse, tags=["LIKES"])
async def like_event(event_id: UUID, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


    existing_like = db.query(Likes).filter_by(user_id=current_user.id, event_id=event_id).first()
    if existing_like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already liked")


    new_like = Likes(user_id=current_user.id, event_id=event_id, created_at=datetime.now(timezone.utc))
    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return LikeResponse(user_id=current_user.id, event_id=event_id, created_at=new_like.created_at)


@like_router.delete("/events/{event_id}/unlike", status_code=status.HTTP_204_NO_CONTENT, tags=["LIKES"])
async def unlike_event(event_id: UUID, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    like = db.query(Likes).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found")

    db.delete(like)
    db.commit()

    return

# Get event details along with like count
@like_router.get("/events/likes/{event_id}", response_model=EventWithLikes, tags=["LIKES"])
async def get_event_with_likes(event_id: UUID, db: db_dependency):
    event = db.query(Events).filter_by(id=event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    like_count = db.query(Likes).filter_by(event_id=event_id).count()

    return EventWithLikes(id=event.id, event_name=event.event_name, event_description=event.event_description, like_count=like_count)











