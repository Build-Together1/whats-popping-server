from typing import List, Dict, Any

from app.apis.auth.schemas import EmailSchema
from app.config import settings
from fastapi import BackgroundTasks, HTTPException, status
from fastapi_mail import ConnectionConfig, MessageSchema, FastMail

from pydantic import EmailStr, BaseModel

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="What's Popping",
    MAIL_TLS=settings.MAIL_TLS,
    MAIL_SSL=settings.MAIL_SSL,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER='app/templates/verification',
)


def send_email(background_tasks: BackgroundTasks, email: EmailSchema):
    template = f"""
        <!DOCTYPE html>
        <html>
        <head>
        </head>
        <body>
            <div style=" display: flex; align-items: center; justify-content: center; flex-direction: column;">
                <h3> Account Verification </h3>
                <br>
                <p>Thanks for joining What's Popping, please 
                enter the OTP below to verify your account</p> 

                <p style="margin-top:1rem;">If you did not register for EasyShopas, 
                please kindly ignore this email and nothing will happen. Thanks<p>
            </div>
        </body>
        </html>
    """

    message = MessageSchema(
        subject="What's Popping Account Verification Mail",
        recipients=email.dict().get("email"),
        body=template,
        subtype="html"
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message, template_name="verify.html")
