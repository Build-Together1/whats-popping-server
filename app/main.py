from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.exceptions.base_exception import BusinessException

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BusinessException)
def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=418,
        content={
            "status code": exc.status_code,
            "detail": exc.detail
        },
    )


@app.get("/")
def index():
    message = {"message": "Welcome to 21Carts"}
    return message
