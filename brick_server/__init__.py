import pdb
import json
import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from .services.entities import entity_router
from .services.data import data_router
from .services.queries import query_router
from .services.actuation import actuation_router

API_V1_PREFIX = '/brickapi/v1'


app = FastAPI(__name__)
app.include_router(data_router, prefix='/brickapi/v1/data')
app.include_router(entity_router, prefix='/brickapi/v1/entities')
app.include_router(query_router, prefix='/brickapi/v1/rawqueries')
app.include_router(actuation_router, prefix='/brickapi/v1/actuation')

app.secret_key = os.urandom(24)
app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))

