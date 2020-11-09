from enum import Enum

from fastapi import HTTPException
from starlette.requests import Request


class RoleLevel(Enum):
    NO_ROLE = 0
    EDITOR = 50
    ADMIN = 100


class UserHasAccessToLevel:
    def __init__(self, role_level: RoleLevel):
        self.role_level = role_level

    def __call__(self, request: Request):
        google_userid = request.session.get('user')
        if not google_userid:
            detail = {
                'err': 'ERROR_USER_NOT_LOGGED_IN',
                'msg': "current user is not logged in"
            }
            raise HTTPException(
                status_code=401,
                detail=detail
            )
        user_role = get_user_role(google_userid)
        if user_role.value < self.role_level.value:
            detail = {
                'err': 'ERROR_USER_NOT_AUTHORIZED',
                'msg': 'user not authorized to access this resource: '
                       f'user has {user_role}, but {self.role_level} is required.'
            }
            raise HTTPException(
                status_code=403,
                detail=detail
            )
        return True


def get_user_role(google_userid):
    # query users collection to get role associated with userid
    # raise HTTPException if no such user exists in the db
    return RoleLevel.ADMIN  # could get int back from query i.e. 50
