from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OPENID_CONFIG_URL
from mongo import get_barkeep_coll
from roles import RoleLevel, DEFAULT_ROLE_LEVEL


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


def get_user_by_google_userid(google_userid):
    # query users collection to get role associated with userid
    coll = get_barkeep_coll('users')
    user = coll.find_one({'userid': google_userid})
    return user


@router.get('/login')
async def login(request: Request):
    if request.session.get('user') and request.session['user']\
            .get('google_userid') and request.session['user'].get('role'):
        return RedirectResponse(url='/')
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/auth')
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    parsed_token = await oauth.google.parse_id_token(request, token)
    google_userid = dict(parsed_token)['sub']
    user = get_user_by_google_userid(google_userid)
    if not user:
        redirect_uri = request.url_for('register')
        return RedirectResponse(url=redirect_uri)
    try:
        user_role = RoleLevel(user.get('role'))
    except ValueError:
        detail = {
            'err': 'ERROR_USER_HAS_INVALID_ROLE',
            'msg': f'user role {user["role"]} is unknown'
        }
        raise HTTPException(
            status_code=404,
            detail=detail
        )

    request.session['user'] = {
        'google_userid': google_userid,
        'role': user_role
    }
    return RedirectResponse(url='/')


@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


@router.post('/register')
async def register(request: Request):
    google_userid = request.session.get('user', {}).get('google_userid')
    if not google_userid:
        redirect_uri = request.url_for('login')
        return RedirectResponse(url=redirect_uri)
    # insert the user into the users collection if they don't exist
    coll = get_barkeep_coll('users')
    user = coll.find_one({'userid': google_userid})
    if user:
        role_level = RoleLevel(user['role'])
    else:
        role_level = DEFAULT_ROLE_LEVEL
        coll.insert_one({'google_userid': google_userid, 'role_level': role_level})
    request.session['user'] = {
        'google_userid': google_userid,
        'role': role_level,
    }

    return RedirectResponse(url='/')
