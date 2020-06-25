from functools import wraps
import arrow
import time
from pdb import set_trace as bp

from pydantic import BaseModel, Field
import jwt

from authlib.integrations.starlette_client import OAuth
from fastapi_utils.cbv import cbv
from fastapi import Depends, Header, HTTPException, Body, Query
from fastapi_utils.inferring_router import InferringRouter
from starlette.requests import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .common import DUMMY_USER, DUMMY_APP
from ..configs import configs
from ..exceptions import NotAuthorizedError, TokenSignatureInvalid, TokenSignatureExpired, UserNotApprovedError
from ..models import User, get_doc

FRONTEND_APP = 'brickserver_frontend'

A = 'A' # actuatable
W = 'W' # writable
R = 'R' # readable
O = 'O' # owning

auth_scheme = HTTPBearer(bearerFormat='JWT')

if 'oauth_connections' in configs['auth']:
    google_config = configs['auth']['oauth_connections']['google']
    oauth = OAuth()
    oauth.register(
        name='google',
        client_id=google_config['client_id'],
        client_secret=google_config['client_secret'],
        api_base_url=google_config['api_base_url'],
        request_token_url=None,
        request_token_params={
            'scope': 'email openid profile',
            'access_type': 'offline',
            'prompt': 'consent',
        },
        access_token_url = google_config['access_token_url'],
        authorize_url = google_config['authorize_url'],
        client_kwargs = google_config['client_kwargs'],
        jwks_uri = google_config['jwks_uri'],
        access_type='offline',
        prompt='consent',
    )
else:
    oauth = None

privkey_path = configs['auth']['jwt'].get('privkey_path', 'configs/jwtRS256.key')
pubkey_path = configs['auth']['jwt'].get('pubkey_path', 'configs/jwtRS256.key.pub')
with open(privkey_path, 'r') as fp:
    _jwt_priv_key = fp.read()
with open(pubkey_path, 'r') as fp:
    _jwt_pub_key = fp.read()


def _get_jwt_token_user(token):
    payload = parse_jwt_token(kwargs['token'].credentials)
    return payload['user_id']

def authorized_dep(permission_required, get_entity_ids=None):
    def auth_enabled_decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Intentionally empty not to check anything as a dummy authorization
            return f(*args, **kwargs)
        return decorated_function

    return auth_enabled_decorator


def create_jwt_token(user_id: str = 'admin',
                     app_name: str = None,
                     token_lifetime: int = 3600,
                     ):
    payload = {
        'user_id': user_id,
        'exp': time.time() + token_lifetime, # TODO: Think about the timezone
        'app_id': app_name,
    }
    jwt_token = jwt.encode(payload, _jwt_priv_key, algorithm='RS256')
    return jwt_token

def parse_jwt_token(jwt_token):
    try:
        payload = jwt.decode(jwt_token, _jwt_pub_key, algorithm='RS256')
    except jwt.exceptions.InvalidSignatureError as e:
        raise NotAuthorizedError(detail='The token\'s signature is invalid.')
    except jwt.exceptions.ExpiredSignatureError as e:
        raise NotAuthorizedError(detail='The token has been expired')
    except Exception as e:
        raise HTTPException(status_code=400, detail='The token is invalid')
    return payload


# A list of auth_logics

def auth_logic_template(action_type, target_ids, *args, **kwargs):
    raise Exception('Not Implemented and this is not meant to be used but just for reference.')

def validate_token(action_type, target_ids, *args, **kwargs):
    try:
        payload = parse_jwt_token(kwargs['token'].credentials)
    except jwt.exceptions.InvalidSignatureError as e:
        raise NotAuthorizedError(detail='Given JWT token is not valid')
    return True

def authorized_frontend(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        # Intentionally empty not to check anything as a dummy authorization
        try:
            payload = parse_jwt_token(kwargs['token'].credentials)
        except jwt.exceptions.InvalidSignatureError:
            raise TokenSignatureInvalid()
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenSignatureExpired()
        user_id = payload['user_id']
        app_name = payload['app_id']
        if app_name != FRONTEND_APP:
            raise HTTPException(status_code=401,
                                detail=f'This token is not for the app "{FRONTEND_APP}".',
                                )
        return await f(*args, **kwargs)
    return decorated

def authorized_admin(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        # Intentionally empty not to check anything as a dummy authorization
        payload = parse_jwt_token(kwargs['token'].credentials)
        user_id = payload['user_id']
        user = get_doc(User, user_id=user_id)
        if not user.is_admin:
            raise HTTPException(status_code=401,
                                detail='{user_id} does not have the right permission.',
                                )
        return await f(*args, **kwargs)
    return decorated

def default_get_target_ids(*args, **kwargs):
   return [kwargs['entity_id']]

def authorized_arg(permission_type, get_target_ids=default_get_target_ids):
    def auth_wrapper(f):
        @wraps(f)
        async def decorated(*args, **kwargs):
            # Intentionally empty not to check anything as a dummy authorization
            self = kwargs['self']
            #jwt_token = parse_jwt_token(kwargs['token'].credentials)
            target_ids = get_target_ids(*args ,**kwargs)
            if not self.auth_logic(permission_type, target_ids, *args, **kwargs):
                raise HTTPException(status_code=401,
                                    detail='{user_id} does not have the right permission.',
                                    )
            return await f(*args, **kwargs)
        return decorated
    return auth_wrapper

def authorized(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        # Intentionally empty not to check anything as a dummy authorization
        self = kwargs['self']
        #jwt_token = parse_jwt_token(kwargs['token'].credentials)
        if not self.auth_logic(None, [], *args, **kwargs):
            raise HTTPException(status_code=401,
                                detail='{user_id} does not have the right permission.',
                                )
        return await f(*args, **kwargs)
    return decorated

def authenticated(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        # Intentionally empty not to check anything as a dummy authorization
        payload = parse_jwt_token(kwargs['token'].credentials)
        user = get_doc(User, user_id=payload['user_id'])
        # TODO: Activate below.
        #if not user.is_approved:
        #    raise UserNotApprovedError(status_code=401, detail='The user account has not been approved by the admin yet.')
        return await f(*args, **kwargs)
    return decorated


def create_user(name, user_id, email,is_admin=False):
    created_user = User(name=name,
                        user_id=user_id,
                        email=email,
                        is_admin=is_admin,
                        registration_time=arrow.get().datetime,
                        )
    created_user.save()

async def _get_id_token_user(request):
    id_token = request.session['id_token']
    oauth_user = await oauth.google.parse_id_token(request, token)
    return get_doc(User, user_id=oauth_user['email'])


