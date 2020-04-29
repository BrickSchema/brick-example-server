import time

import arrow
from fastapi_utils.inferring_router import InferringRouter
from fastapi import Depends, Header, HTTPException, Body, Query, Path
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request

from .configs import configs
from .auth.authorization import create_user, oauth

frontend_hostname = configs['frontend'].get('hostname', configs['hostname'])
loggedin_frontend = frontend_hostname + '/loggedin_page'


dummy_frontend_router = InferringRouter('dummy-frontend')

@dummy_frontend_router.get('/loggedin_page') # TODO: This is supposed to be a main page for the user in the frontend.
def get_dummy_register_user(request: Request,
                            app_token: str,
                            ):
    return f'Frontend App token: {app_token}'

login_link_tag = '<a href="{0}/auth/login">login</a>'.format(configs['hostname'])
@dummy_frontend_router.get('/main')
def login_main(request: Request,
               response_class: HTMLResponse,
               ):
    return HTMLResponse(login_link_tag)


@dummy_frontend_router.get('/register')
def login_main(request: Request,
               name: str,
               email: str,
               ):
    return HTMLResponse('Please register here')
