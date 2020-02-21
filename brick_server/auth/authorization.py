from functools import wraps
import time
import pdb

from pydantic import BaseModel, Field
import jwt

from fastapi_utils.cbv import cbv
from fastapi import Depends, Header, HTTPException, Body, Query
from fastapi_utils.inferring_router import InferringRouter
from starlette.requests import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .common import DUMMY_USER, DUMMY_APP
from ..configs import configs


A = 'A' # actuatable
W = 'W' # writable
R = 'R' # readable
O = 'O' # owning

auth_scheme = HTTPBearer()

with open(configs['auth']['jwt']['privkey_path'], 'r') as fp:
    _jwt_priv_key = fp.read()
with open(configs['auth']['jwt']['pubkey_path'], 'r') as fp:
    _jwt_pub_key = fp.read()


def authorized(permission_required, get_entity_ids=None):
    def auth_enabled_decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Intentionally empty not to check anything as a dummy authorization
            pdb.set_trace()
            return f(*args, **kwargs)
        return decorated_function

    return auth_enabled_decorator


def create_jwt_token(token_lifetime: int = 3600):
    payload = {
        'user_id': 'admin',
        'exp': time.time() + token_lifetime # TODO: Think about the timezone
    }
    jwt_token = jwt.encode(payload, _jwt_priv_key, algorithm='RS256')
    return jwt_token

def parse_jwt_token(jwt_token):
    payload = jwt.decode(jwt_token, _jwt_pub_key, algorithm='RS256')
    return payload

def authorized_isadmin(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        # Intentionally empty not to check anything as a dummy authorization
        payload = parse_jwt_token(kwargs['token'].credentials)
        user_id = payload['user_id']
        if user_id != 'admin':
            raise HTTPException(status_code=401,
                                detail='{user_id} does not have the right permission.',
                                )
        return await f(*args, **kwargs)
    return decorated
