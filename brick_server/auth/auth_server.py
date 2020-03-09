import time
import arrow
import requests

from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv
from fastapi import Depends, Header, HTTPException, Body, Query, Path, Form
#from fastapi.responses import PlainTextResponse
from starlette.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from starlette.requests import Request

from ..configs import configs
from .authorization import FRONTEND_APP, oauth, _get_user, authenticated, _jwt_pub_key
from .models import TokensResponse, TokenResponse
from ..dummy_frontend import loggedin_frontend
from ..exceptions import DoesNotExistError
from ..models import get_doc, User

from pdb import set_trace as bp



auth_router = InferringRouter('auth')
auth_base_url = configs['hostname'] + '/auth'

@auth_router.get('/jwt_pubkey',
                 status_code=200,
                 description='Get the current JWT Public Key',
                 tags=['Auth'],
                 )
def get_jwt_pubkey():
    return PlainTextResponse(_jwt_pub_key, media_type='text/plain')

@auth_router.get('/login',
                 tags=['Auth'],
                 )
async def get_login_via_google(request: Request):
    redirect_url = auth_base_url + '/is_registered'
    res = await oauth.google.authorize_redirect(request, redirect_url)
    return res

@auth_router.get('/is_registered',
                 status_code=302,
                 response_class=RedirectResponse,
                 tags=['Auth'],
                 )
async def get_is_registered(request: Request):
    token = await oauth.google.authorize_access_token(request)
    t0 = time.time()
    user = await oauth.google.parse_id_token(request, token)
    t1 = time.time()
    print('parsing token took: {0} seconds'.format(t1 - t0))
    params = {
        'access_token': token['access_token'],
    }
    #resp = requests.get(oauth.google.api_base_url + '/userinfo', params=params)
    request.session['id_token'] = token
    assert user['email_verified']
    try:
        user_doc = get_doc(User, userid=user['email'])
    except DoesNotExistError:
        return RedirectResponse(auth_base_url + '/register') #TODO: This should be changed to the frontend page for registratino.
    return RedirectResponse(loggedin_frontend)

@auth_router.get('/logincallback') # NOTE: Dummy function
async def get_authorize(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    request.session['id_token'] = token
    return dict(user)

@cbv(auth_router)
class AppTokensRouter(object):
    @auth_router.post('/app_tokens',
                      status_code=200,
                      tags=['Auth'],
                      )
    @authenticated
    async def gen_token(request: Request,
                        app_name: str = Query(FRONTEND_APP,
                                              description='The name of an app the user needs to generate a token for'),
                        ) -> TokenResponse:
        user = _get_user(request)
        jwt_token = create_jwt_token(app_name=app_name)
        user.app_tokens.append(jwt_token)
        user.save()
        return jwt_token

    @auth_router.get('/app_tokens',
                      status_code=200,
                      tags=['Auth'],
                     response_model=TokensResponse,
                     )
    @authenticated
    async def get_tokens(request: Request) -> TokensResponse:
        user = _get_user(request)
        tokens = user.app_tokens
        valid_tokens = [token for token in tokens
                        if parse_jwt_token(token)['exp'] < time.time()]
        user.app_tokens = valid_tokens
        user.save()
        return valid_tokens


# NOTE: This is the API to register a user.
@auth_router.get('/register',
                 status_code=302,
                 response_class=RedirectResponse,
                 tags=['Auth'],
                 )
async def post_register_user(request: Request,
                             is_admin: bool=Form(False, description='Designate if the user is going to be an admin or not.'),
                             ):
    # TODO: Check if is_admin is allowed somwehow. (Maybe endorsed by the first admin or check the number of admins in the database and allow only one.
    token = request.session['id_token']
    oauth_user = await oauth.google.parse_id_token(request, token)
    profile = (await oauth.google.get('userinfo', token=token)).json()

    if is_admin:
        assert User.objects.count(is_admin=True) == 0, 'There is already an existnig admin, and Brick Server currently allows only on eadmin'
        is_approved = True
    else:
        is_approved = False
    new_user = User(name=profile['name'],
                    userid=oauth_user['email'],
                    email=oauth_user['email'],
                    is_admin=is_admin,
                    is_approved=False,
                    registration_time=arrow.get().datetime
                    )
    new_user.save()
    return RedirectResponse(loggedin_frontend)
