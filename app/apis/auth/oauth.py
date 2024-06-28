import json

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.config import settings
from starlette.config import Config

# from starlette.config import Config


google_auth_router = APIRouter(tags=["GOOGLE AUTHENTICATION"])
# oauth.add_middleware(SessionMiddleware, secret_key="!secret")

client_id = settings.CLIENT_ID

client_secret = settings.CLIENT_SECRET

# config = Config('.env')
# oauth = OAuth(config)

oauth = OAuth()

CONF_URL = settings.CONF_URL
oauth.register(
    name=settings.NAME,
    server_metadata_url=CONF_URL,
    client_id=client_id,
    client_secret=client_secret,
    authorize_url=settings.AUTHORIZE_URL,
    access_token_url=settings.ACCESS_TOKEN_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@google_auth_router.get("/")
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/logout">logout</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')


@google_auth_router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@google_auth_router.get("/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    # return JSONResponse(content={"user": user})
    return RedirectResponse(url='/')


@google_auth_router.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')
