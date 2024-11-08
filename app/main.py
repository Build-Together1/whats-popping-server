from typing import Annotated

from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.apis.auth.oauth import google_auth_router
from app.apis.auth.routes import auth_router
from app.apis.users.routes import user_router
from app.apis.events.event_route import event_router
from app.apis.events.comment_route import comment_router
from app.apis.events.like_route import like_router
from app.database import models
from app.database.session import get_db, engine
from app.exceptions.base_exception import BusinessException, CredentialsException

# from app.utils.custom_openapi import custom_openapi

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="What's Popping Event Platform API",
    version="1.0.0",
    description="API for an event platform."
)
app.include_router(google_auth_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(event_router)
app.include_router(comment_router)
app.include_router(like_router)



# app.openapi = lambda: custom_openapi(app)

db_dependency = Annotated[Session, Depends(get_db)]

# origins = [
#     "http://localhost:8080",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key="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")


@app.exception_handler(BusinessException)
def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=418,
        content={
            "status code": exc.status_code,
            "detail": exc.detail
        },
    )


@app.exception_handler(CredentialsException)
def credentials_exception_handler(request: Request, exc: CredentialsException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "status code": exc.status_code,
            "detail": exc.detail,
            "headers": exc.headers
        },
    )

