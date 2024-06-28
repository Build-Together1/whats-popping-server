from typing import Annotated

from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

# from app.utils.custom_openapi import custom_openapi

from app.apis.auth.oauth import google_auth_router
from app.apis.auth.individual.routes import individual_auth_router
from app.apis.auth.corporate.routes import corporate_auth_router
from app.apis.auth.routes import auth_router
from app.apis.users.corporate.routes import corporate_router
from app.apis.users.individual.routes import individual_router
from app.exceptions.base_exception import BusinessException, CredentialsException
from app.database.session import get_db

app = FastAPI(
    title="What's Popping Event Platform API",
    version="1.0.0",
    description="API for an event platform."
)

app.include_router(google_auth_router)
app.include_router(auth_router)
app.include_router(individual_router)
app.include_router(individual_auth_router)
app.include_router(corporate_router)
app.include_router(corporate_auth_router)


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

#
# @app.get("/", tags=["HOME"])
# def index():
#     message = {"message": "Welcome to Popping"}
#     return message

# @individual_auth_router.delete("/otp-codes", status_code=status.HTTP_200_OK)
# async def delete_otp_codes(db: db_dependency):
#     otp_delete = db.query(OTPCodes).all()
#
#     for otp in otp_delete:
#         db.delete(otp)
#     db.commit()
#
#     return {"message": "Users deleted successfully"}
#
#
# @individual_auth_router.delete("/delete-pass-otp", status_code=status.HTTP_200_OK)
# async def delete_password_otp(db: db_dependency):
#     reset_codes = db.query(PasswordReset).all()
#
#     for code in reset_codes:
#         db.delete(code)
#     db.commit()
#
#     return {"message": "Users deleted successfully"}

# @app.put("/update-user", response_model=UserResponse)
# async def create_user(user_id: str, req: UserUpdate, db: db_dependency):
#     user_query = db.query(BaseUser).filter(user_id == BaseUser.id)
#
#     user = user_query.first()
#
#     if not user:
#         return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#
#     user_dict = req.model_dump(exclude_unset=True)
#
#     user_query.update(req.model_dump(exclude_unset=True), synchronize_session=False)
#
#     db.commit()
#
#     return user


# user_dict = req.model_dump(exclude_unset=True)
# user_model_dict = jsonable_encoder(user)
#
# for key in user_model_dict:
#     if key in user_dict:
#         setattr(user, key, user_dict.get(key))
#
# db.add(user)
# db.commit()
# db.refresh(user)
#
# return user
