from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from ..config import settings

# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:ignite@localhost/poppingDB"

# settings = get_settings()

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USERNAME}:" \
                          f"{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}" \
                          f":{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
