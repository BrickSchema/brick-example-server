import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_rest_framework import config, logging
from fastapi_utils.timing import add_timing_middleware
from loguru import logger
from starlette.middleware.sessions import SessionMiddleware

from brick_server.minimal.config import FastAPIConfig

settings = config.init_settings(FastAPIConfig)

from brick_server.minimal.auth.authorization import default_auth_logic
from brick_server.minimal.dependencies import update_dependency_supplier

update_dependency_supplier(default_auth_logic)

API_V1_PREFIX = "/brickapi/v1"

logging.init_logging()
logging.intercept_all_loggers()
app = FastAPI(title="Brick Server", openapi_url="/docs/openapi.json")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_timing_middleware(app, record=logger.info)
app.logger = logger


@app.on_event("startup")
async def startup_event() -> None:
    from brick_server.minimal.init import initialization

    await initialization()


from .auth.auth_server import auth_router
from .services.actuation import actuation_router
from .services.data import data_router
from .services.domain import domain_router
from .services.entities import entity_router
from .services.grafana import grafana_router
from .services.queries import query_router

app.include_router(data_router, prefix="/brickapi/v1/data")
app.include_router(domain_router, prefix="/brickapi/v1/domains")
app.include_router(entity_router, prefix="/brickapi/v1/entities")
app.include_router(query_router, prefix="/brickapi/v1/rawqueries")
app.include_router(actuation_router, prefix="/brickapi/v1/actuation")
app.include_router(grafana_router, prefix="/brickapi/v1/grafana")
app.include_router(auth_router, prefix="/brickapi/v1/auth")
# app.include_router(dummy_frontend_router, prefix='/dummy-frontend')

app.secret_key = os.urandom(24)
app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))
