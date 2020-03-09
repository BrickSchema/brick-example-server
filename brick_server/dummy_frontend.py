import time

import arrow
from fastapi_utils.inferring_router import InferringRouter
from fastapi import Depends, Header, HTTPException, Body, Query, Path
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request

from .configs import configs
from .auth.authorization import create_user, oauth

from pdb import set_trace as bp

frontend_hostname = configs['frontend']['hostname']
loggedin_frontend = frontend_hostname + '/loggedin_page'


dummy_frontend_router = InferringRouter('dummy-frontend')

@dummy_frontend_router.get('/loggedin_page') # TODO: This is supposed to be a main page for the user in the frontend.
def get_dummy_register_user(request: Request):
    return 'successful'

@dummy_frontend_router.get('/main')
def login_main(request: Request,
               response_class: HTMLResponse,
               ):
    return HTMLResponse('<a href="https://bd-testbed.ucsd.edu:8000/auth/login">login</a>')
