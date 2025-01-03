from typing import Annotated
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import joinedload, selectinload

from app.apis.auth.schemas import UserLogin
from app.apis.auth.services import UserAccount
from app.apis.events.schemas import (
    EventCreate, EventPublic, EventUpdate, CommentPublic,
    UserWithEvents
)
from app.database.models import User, Events
from app.database.session import db_dependency
from .schemas import EventWithLikes

event_router = APIRouter(tags=["EVENTS"])

auth_dependency = Annotated[UserLogin, Depends(UserAccount.get_current_active_user)]


@event_router.post(
    "/events/", status_code=status.HTTP_201_CREATED
)
async def add_event(
        req: EventCreate,
        db: db_dependency,
        current_user: auth_dependency
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    event_dict = req.model_dump()
    # account = crud.save_account_to_db(user_dict, db)
    event = Events(
        **event_dict,
        user_id=current_user.id
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@event_router.get(
    "/events/{event_id}",
    status_code=status.HTTP_200_OK,
    response_model=EventPublic,
)
async def get_event(event_id: UUID, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    event = db.query(Events).filter(Events.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event does not exist")

    return event


@event_router.patch("/events/{event_id}", response_model=EventPublic)
def update_event(event_id: UUID, req: EventUpdate, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    event = db.query(Events).filter(Events.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event does not exist")

    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


@event_router.delete(
    "/events/{event_id}", status_code=status.HTTP_200_OK
)
async def delete_event(event_id: UUID, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    event = db.query(Events).filter(Events.id == event_id)
    if not event.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="event does not exist")

    event.delete(synchronize_session=False)
    db.commit()

    return {"message": "Deleted successfully"}


# @event_router.get("/events/{user_id}", response_model=UserWithEvents)
# async def get_user_with_events(user_id: UUID, db: db_dependency):
#     user = db.query(User).options(
#         selectinload(User.events).selectinload(Events.comments)
#     ).filter(User.id == user_id).first()
#
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     user_data = UserWithEvents(
#         name=user.name,
#         username=user.username,
#         profile_header_path=user.profile_header_path,
#         profile_pic_path=user.profile_pic_path,
#         location=user.location,
#         website=user.website,
#         events=[
#             EventPublic(
#                 event_name=event.event_name,
#                 event_description=event.event_description,
#                 event_category=event.event_category,
#                 event_image=event.event_image,
#                 event_date=event.event_date,
#                 event_time=event.event_time,
#                 event_location=event.event_location,
#                 comments=[CommentPublic(content=comment.content) for comment in event.comments],
#             )
#             for event in user.events
#         ]
#     )
#
#     return user_data

@event_router.get(
    "/events/", status_code=status.HTTP_200_OK, response_model=List[EventPublic]
)
async def get_all_events(db: db_dependency):
    events = db.query(Events).options(joinedload(Events.comments)).all()

    events_with_comments = [
        EventPublic(
            **event.__dict__,
            Comments=[CommentPublic(id=comment.id, content=comment.content) for comment in event.comments],
            likes=[EventWithLikes(like_count=len(event.likes))]

        )
        for event in events
    ]

    return events_with_comments


@event_router.get("/user/events/{user_id}", response_model=UserWithEvents)
async def get_user_with_events_and_likes(user_id: UUID, db: db_dependency):
    # Query User and eagerly load Events, Comments, and Likes relationships
    user = db.query(User).options(
        # Load events associated with the user
        joinedload(User.events)
    ).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Load comments and likes for each event in a second query to ensure proper relationship loading
    events_with_details = []
    for event in user.events:
        event_with_comments_and_likes = db.query(Events).options(
            selectinload(Events.comments),  # Load comments for this event
            selectinload(Events.likes)  # Load likes for this event
        ).filter(Events.id == event.id).first()

        if event_with_comments_and_likes:
            # Count the number of likes for the event
            like_count = len(event_with_comments_and_likes.likes)

            # Build event data with likes and comments
            events_with_details.append(
                EventPublic(
                    id=event.id,
                    event_name=event_with_comments_and_likes.event_name,
                    event_description=event_with_comments_and_likes.event_description,
                    event_category=event_with_comments_and_likes.event_category,
                    event_image=event_with_comments_and_likes.event_image,
                    event_date=event_with_comments_and_likes.event_date,
                    event_time=event_with_comments_and_likes.event_time,
                    event_location=event_with_comments_and_likes.event_location,
                    comments=[CommentPublic(content=comment.content) for comment in
                              event_with_comments_and_likes.comments],
                    likes=[EventWithLikes(like_count=like_count)]  # Add like count here
                )
            )

    user_data = UserWithEvents(
        name=user.name,
        username=user.username,
        profile_header_path=user.profile_header_path,
        profile_pic_path=user.profile_pic_path,
        location=user.location,
        website=user.website,
        events=events_with_details
    )

    return user_data


@event_router.delete(
    "/events", status_code=status.HTTP_200_OK
)
async def delete_events(db: db_dependency):
    events = db.query(Events).all()

    for event in events:
        db.delete(event)
    db.commit()

    return {"message": "events deleted successfully"}
