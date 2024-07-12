# import json
# from fastapi import FastAPI, Depends, Request, Form, HTTPException
# from starlette.responses import HTMLResponse, RedirectResponse
# from starlette.middleware.sessions import SessionMiddleware
# from authlib.integrations.starlette_client import OAuth, OAuthError
# from sqlalchemy.orm import Session
# from database import engine, Base, get_db
# from models import User
# from starlette.config import Config
#
# # Load environment variables
# config = Config('.env')
# GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
# GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET')
# SECRET_KEY = config('SECRET_KEY')
#
# # Initialize FastAPI app
# app = FastAPI()
# app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
#
# # Initialize OAuth
# oauth = OAuth(config)
# CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
# oauth.register(
#     name='google',
#     client_id=GOOGLE_CLIENT_ID,
#     client_secret=GOOGLE_CLIENT_SECRET,
#     server_metadata_url=CONF_URL,
#     client_kwargs={'scope': 'openid email profile'}
# )
#
# # Create database tables
# Base.metadata.create_all(bind=engine)
#
# @app.get('/')
# async def homepage(request: Request):
#     user = request.session.get('user')
#     if user:
#         data = json.dumps(user)
#         html = f'<pre>{data}</pre><a href="/logout">logout</a>'
#         return HTMLResponse(html)
#     return HTMLResponse('<a href="/login">login</a>')
#
# @app.get('/login')
# async def login(request: Request):
#     redirect_uri = request.url_for('auth')
#     return await oauth.google.authorize_redirect(request, redirect_uri)
#
# @app.get('/auth')
# async def auth(request: Request, db: Session = Depends(get_db)):
#     try:
#         token = await oauth.google.authorize_access_token(request)
#     except OAuthError as error:
#         return HTMLResponse(f'<h1>{error.error}</h1>')
#
#     user_info = token.get('userinfo')
#     if user_info:
#         google_sub = user_info['sub']
#         user = db.query(User).filter(User.google_sub == google_sub).first()
#
#         if not user:
#             request.session['temp_user'] = user_info
#             return RedirectResponse(url='/signup')
#         else:
#             request.session['user'] = {
#                 "id": user.id,
#                 "email": user.email,
#                 "name": user.name,
#                 "username": user.username
#             }
#             return RedirectResponse(url='/')
#
#     return HTMLResponse('<h1>Authentication failed</h1>')
#
# @app.get('/signup')
# async def signup_form(request: Request):
#     temp_user = request.session.get('temp_user')
#     if not temp_user:
#         return RedirectResponse(url='/')
#
#     return HTMLResponse(
#         '<form action="/signup" method="post">'
#         'Username: <input type="text" name="username"><br>'
#         '<input type="submit" value="Sign Up">'
#         '</form>'
#     )
#
# @app.post('/signup')
# async def signup(request: Request, db: Session = Depends(get_db), username: str = Form(...)):
#     temp_user = request.session.get('temp_user')
#     if not temp_user or not username:
#         return RedirectResponse(url='/')
#
#     google_sub = temp_user['sub']
#     if db.query(User).filter(User.username == username).first():
#         raise HTTPException(status_code=400, detail="Username already taken")
#
#     user = User(
#         google_sub=google_sub,
#         email=temp_user['email'],
#         name=temp_user['name'],
#         username=username
#     )
#     db.add(user)
#     db.commit()
#
#     request.session['user'] = {
#         "id": user.id,
#         "email": user.email,
#         "name": user.name,
#         "username": user.username
#     }
#     request.session.pop('temp_user', None)
#     return RedirectResponse(url='/')
#
# @app.get('/logout')
# async def logout(request: Request):
#     request.session.pop('user', None)
#     return RedirectResponse(url='/')
#
#
#
#     from sqlalchemy import Column, Integer, String
# from database import Base
#
# class User(Base):
#     __tablename__ = 'users'
#
#     id = Column(Integer, primary_key=True, index=True)
#     google_sub = Column(String, unique=True, index=True, nullable=True)
#     email = Column(String, unique=True, index=True)
#     name = Column(String)
#     username = Column(String, unique=True, index=True)
#
#
#
#
#
#
# from fastapi import FastAPI
# from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
# from starlette.requests import Request
# from starlette.responses import JSONResponse
# from pydantic import EmailStr, BaseModel
# from typing import List
# app = FastAPI()
#
#
# conf = ConnectionConfig(
#    MAIL_USERNAME=from_,
#    MAIL_PASSWORD="************",
#    MAIL_PORT=587,
#    MAIL_SERVER="smtp.gmail.com",
#    MAIL_TLS=True,
#    MAIL_SSL=False
# )
#
#
# message = MessageSchema(
#        subject="Fastapi-Mail module",
#        recipients=email.dict().get("email"),  # List of recipients, as many as you can pass
#        body=template,
#        subtype="html"
#        )
#
#
# fm = FastMail(conf)
# await fm.send_message(message)
#
#
# app.post("/send_mail")
#
# async def send_mail(email: EmailSchema):
#
#
#     template = """
#
#         <html>
#
#         <body>
#
#
#
# <p>Hi !!!
#
#         <br>Thanks for using fastapi mail, keep using it..!!!</p>
#
#
#
#         </body>
#
#         </html>
#
#         """
#
#
#     message = MessageSchema(
#
#         subject="Fastapi-Mail module",
#
#         recipients=email.dict().get("email"),  # List of recipients, as many as you can pass
#
#         body=template,
#
#         subtype="html"
#
#         )
#
#
#     fm = FastMail(conf)
#
#     await fm.send_message(message)
#
#         print(message)
#
#
#
#
#
#     return JSONResponse(status_code=200, content={"message": "email has been sent"}
#
#
#
# @app.post("/emailbackground")
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
#
#     fm = FastMail(conf)
#
#     background_tasks.add_task(fm.send_message,message)
#
#     return JSONResponse(status_code=200, content={"message": "email has been sent"})
#
#
#
# class EmailSchema(BaseModel):
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
#
#
#
#
#
