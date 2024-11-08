from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi import status

from app.apis.auth.schemas import UserLogin
from app.apis.auth.services import UserAccount
from app.apis.events.schemas import (
    CommentCreate, CommentPublic,
    CommentUpdate
)
from app.database.models import Events, Comments
from app.database.session import db_dependency

comment_router = APIRouter(tags=["COMMENTS"])

auth_dependency = Annotated[UserLogin, Depends(UserAccount.get_current_active_user)]




@comment_router.post("/comments/{event_id}", response_model=CommentPublic, status_code=status.HTTP_201_CREATED, tags=["COMMENTS"])
async def add_comment(event_id: UUID, req: CommentCreate, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    event = db.query(Events).filter(Events.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="event does not exist")

    comment_dict = req.model_dump()
    comment_data = Comments(**comment_dict, user_id=current_user.id, event_id=event_id)

    db.add(comment_data)
    db.commit()
    db.refresh(comment_data)

    return comment_data



@comment_router.patch("/comments/{comment_id}", response_model=CommentPublic, tags=["COMMENTS"])
def update_comment(comment_id: UUID, req: CommentUpdate, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    comment = db.query(Comments).filter(Comments.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment does not exist")


    comment.content = req.content


    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@comment_router.delete(
    "/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["COMMENTS"])
async def delete_comment(comment_id: UUID, db: db_dependency, current_user: auth_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    comment = db.query(Comments).filter(Comments.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment does not exist")

    comment.delete(synchronize_session=False)
    db.commit()

    return {"message": "Deleted successfully"}




