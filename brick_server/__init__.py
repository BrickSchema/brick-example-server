import pdb
import json
import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from .services.entities import entity_router
from .services.data import data_router
from .services.queries import query_router
from .services.actuation import actuation_router
from .auth.auth_server import auth_router
from .dummy_frontend import dummy_frontend_router

API_V1_PREFIX = '/brickapi/v1'


app = FastAPI(__name__, title='Brick Server', openapi_url='/docs/openapi.json')
app.include_router(data_router, prefix='/brickapi/v1/data')
app.include_router(entity_router, prefix='/brickapi/v1/entities')
app.include_router(query_router, prefix='/brickapi/v1/rawqueries')
app.include_router(actuation_router, prefix='/brickapi/v1/actuation')
app.include_router(auth_router, prefix='/auth')
app.include_router(dummy_frontend_router, prefix='/dummy-frontend')

app.secret_key = os.urandom(24)
app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))
