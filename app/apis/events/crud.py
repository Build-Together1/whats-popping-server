from uuid import UUID

from sqlalchemy.orm import Session
from app.database.models import Likes, Events

def add_like(db: Session, user_id: UUID, event_id: UUID):
    # Check if the like already exists
    existing_like = db.query(Likes).filter_by(user_id=user_id, event_id=event_id).first()
    if existing_like:
        return existing_like  # Return the existing like if already liked

    new_like = Likes(user_id=user_id, event_id=event_id)
    db.add(new_like)
    db.commit()
    db.refresh(new_like)
    return new_like

def remove_like(db: Session, user_id: UUID, event_id: UUID):
    like = db.query(Likes).filter_by(user_id=user_id, event_id=event_id).first()
    if like:
        db.delete(like)
        db.commit()
        return True
    return False

def get_event_like_count(db: Session, event_id: UUID):
    return db.query(Likes).filter_by(event_id=event_id).count()
