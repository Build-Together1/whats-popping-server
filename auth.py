# Password345
# Locked123
# Locked12345
# user10@example.com
# # Corporate13
#
#
#
# Client ID = 564050256646-tvo6ula2j1342k5jg3gbns0f52sn29vb.apps.googleusercontent.com
#
# Client secret = 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
#



#import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
#
# def send_verification_email(to_email: str, token: str):
#     sender_email = "your_email@example.com"
#     sender_password = "your_password"
#     subject = "Verify your email"
#     verify_link = f"http://yourdomain.com/verify/{token}"
#
#     # Create the email content in HTML
#     html_content = f"""
#     <html>
#     <body>
#         <h1>Welcome to Our Service</h1>
#         <p>Thank you for registering. Please click the button below to verify your email address:</p>
#         <p><a href="{verify_link}" style="padding: 10px 20px; color: white; background-color: blue; text-decoration: none;">Verify Email</a></p>
#         <p>If you did not register, please ignore this email.</p>
#     </body>
#     </html>
#     """
#
#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = to_email
#     msg['Subject'] = subject
#
#     msg.attach(MIMEText(html_content, 'html'))
#
#     try:
#         with smtplib.SMTP('smtp.example.com', 587) as server:
#             server.starttls()
#             server.login(sender_email, sender_password)
#             server.sendmail(sender_email, to_email, msg.as_string())
#     except Exception as e:
#         print(f"Error sending email: {e}")
#
#
#
#
#
# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy.orm import Session
# from . import models, schemas, utils, deps, email_utils
# from .database import engine
#
# models.Base.metadata.create_all(bind=engine)
#
# app = FastAPI()
#
# @app.post("/register", response_model=schemas.UserOut)
# def register_user(user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
#     db_user = db.query(models.User).filter(models.User.email == user.email).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     hashed_password = utils.get_password_hash(user.password)
#     db_user = models.User(email=user.email, hashed_password=hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#
#     token = utils.create_access_token({"sub": db_user.email})
#     email_utils.send_verification_email(user.email, token)
#
#     return db_user
#
#
#
#
#
# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user = get_user(fake_users_db, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user
#
#
#
#
#     from sqlalchemy import Column, Integer, String, Boolean, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime
#
# Base = declarative_base()
#
# class User(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True, nullable=False)
#     hashed_password = Column(String, nullable=False)
#     is_active = Column(Boolean, default=False)
#     is_verified = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#
#
#     from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy.orm import Session
# from . import models, schemas, utils, deps, email_utils
# from .database import engine
#
# models.Base.metadata.create_all(bind=engine)
#
# app = FastAPI()
#
# @app.post("/register", response_model=schemas.UserOut)
# def register_user(user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
#     db_user = db.query(models.User).filter(models.User.email == user.email).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     hashed_password = utils.get_password_hash(user.password)
#     db_user = models.User(email=user.email, hashed_password=hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#
#     token = utils.create_access_token({"sub": db_user.email})
#     email_utils.send_verification_email(user.email, token)
#
#     return db_user
#
#
#
#     from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy.orm import Session
# from jose import JWTError, jwt
# from . import models, deps, utils
#
# app = FastAPI()
#
# @app.get("/verify/{token}")
# def verify_email(token: str, db: Session = Depends(deps.get_db)):
#     try:
#         payload = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
#         email = payload.get("sub")
#         if email is None:
#             raise HTTPException(status_code=400, detail="Invalid token")
#         db_user = db.query(models.User).filter(models.User.email == email).first()
#         if db_user is None:
#             raise HTTPException(status_code=404, detail="User not found")
#         db_user.is_verified = True
#         db_user.is_active = True  # Activating the user account upon verification
#         db.commit()
#         db.refresh(db_user)
#         return {"msg": "Email verified"}
#     except JWTError:
#         raise HTTPException(status_code=400, detail="Invalid token")
#
#
#
#  from fastapi import FastAPI, HTTPException, Depends
# from sqlalchemy.orm import Session
# from . import models, deps
#
# app = FastAPI()
#
# @app.post("/deactivate_user/{user_id}")
# def deactivate_user(user_id: int, db: Session = Depends(deps.get_db)):
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     user.is_active = False
#     db.commit()
#     db.refresh(user)
#     return {"msg": "User deactivated successfully"}
#
#
#
#   from fastapi import Depends, HTTPException
#
# def get_current_active_user(user: models.User = Depends(get_current_user)):
#     if not user.is_active:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return user

#
#
#
#     import smtplib
# from email.mime.text import MIMEText
#
# SMTP_SERVER = "smtp.yourserver.com"
# SMTP_PORT = 587
# SMTP_USERNAME = "your_username"
# SMTP_PASSWORD = "your_password"
# EMAIL_FROM = "your_email@example.com"
# EMAIL_SUBJECT = "Email Verification"
#
# def send_verification_email(email_to: str, token: str):
#     msg = MIMEText(f"Please verify your email by clicking on the following link: http://yourdomain.com/verify/{token}")
#     msg["Subject"] = EMAIL_SUBJECT
#     msg["From"] = EMAIL_FROM
#     msg["To"] = email_to
#
#     with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#         server.starttls()
#         server.login(SMTP_USERNAME, SMTP_PASSWORD)
#         server.sendmail(EMAIL_FROM, email_to, msg.as_string())
#
#
#
#
#

#
# app = FastAPI()
#
#
#
# @app.post("/email")
# async def simple_send(email: EmailSchema) -> JSONResponse:
#     html = """<p>Hi this test mail, thanks for using Fastapi-mail</p> """
#
#     message = MessageSchema(
#         subject="Fastapi-Mail module",
#         recipients=email.dict().get("email"),
#         body=html,
#         subtype=MessageType.html)
#
#     fm = FastMail(conf)
#     await fm.send_message(message)
#     return JSONResponse(status_code=200, content={"message": "email has been sent"})
#
#
#
#
#  @app.post("/emailbackground")
# async def send_in_background(
#     background_tasks: BackgroundTasks,
#     email: EmailSchema
#     ) -> JSONResponse:
#
#     message = MessageSchema(
#         subject="Fastapi mail module",
#         recipients=email.dict().get("email"),
#         body="Simple background task",
#         subtype=MessageType.plain)

#         body=html,
#         subtype=MessageType.html)
#
#     fm = FastMail(conf)
#
#     background_tasks.add_task(fm.send_message,message)
#
#     return JSONResponse(status_code=200, content={"message": "email has been sent"})
#
#
#
#
#     #JINJA2 TEMPLATES
#
#     class EmailSchema(BaseModel):
#     email: List[EmailStr]
#     body: Dict[str, Any]
#
# conf = ConnectionConfig(
#     MAIL_USERNAME = "YourUsername",
#     MAIL_PASSWORD = "strong_password",
#     MAIL_FROM = "your@email.com",
#     MAIL_PORT = 587,
#     MAIL_SERVER = "your mail server",
#     MAIL_STARTTLS = True,
#     MAIL_SSL_TLS = False,
#     TEMPLATE_FOLDER = Path(__file__).parent / 'templates',
# )
#
#
# @app.post("/email")
# async def send_with_template(email: EmailSchema) -> JSONResponse:
#
#     message = MessageSchema(
#         subject="Fastapi-Mail module",
#         recipients=email.dict().get("email"),
#         template_body=email.dict().get("body"),
#         subtype=MessageType.html,
#         )
#
#     fm = FastMail(conf)
#     await fm.send_message(message, template_name="email_template.html")
#     return JSONResponse(status_code=200, content={"message": "email has been sent"})
#
# import random
# import string
# from datetime import datetime, timedelta, timezone
#
#
# def generate_otp(expires_delta: timedelta | None = None):
#     digits = string.digits
#     otp = ''.join(random.choice(digits) for _ in range(5))
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=1)
#     otp_termination = {
#         "otp": otp,
#         "expire": expire
#     }
#     return otp_termination

