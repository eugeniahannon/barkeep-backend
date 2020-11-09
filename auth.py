from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OPENID_CONFIG_URL


class AuthError(Exception):
    pass


class NoAuthenticationError(AuthError):
    # there is no authorization (should be called authN) header
    pass


class InvalidTokenError(AuthError):
    # the token received is invalid
    pass


class UserNotFoundError(AuthError):
    # user is not found in users collection
    pass


class UserNotAuthorizedError(AuthError):
    # user is found in the collection but has insufficient privileges
    pass


router = APIRouter()
oauth = OAuth()
oauth.register(
    'google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url=OPENID_CONFIG_URL,
    client_kwargs={
        'scope': 'openid'
    }
)


@router.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/auth')
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    request.session['user'] = dict(user)['sub']
    return RedirectResponse(url='/')


@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')
