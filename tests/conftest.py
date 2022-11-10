import asyncio
from typing import Any, AsyncGenerator, Generator

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi_rest_framework.config import settings
from httpx import AsyncClient

from brick_server.minimal.app import app as fastapi_app
from brick_server.minimal.auth.authorization import create_jwt_token
from brick_server.minimal.interfaces.graphdb import GraphDB
from brick_server.minimal.models import User
from brick_server.minimal.schemas import Domain
from tests.common import DOMAIN_BASE, TEST_DOMAIN_NAME
from tests.utils import (
    create_postgres_db,
    drop_mongodb,
    drop_postgres_db,
    ensure_graphdb_brick_schema,
    register_admin,
)


@pytest.yield_fixture(scope="session")
def event_loop(request: Any) -> Generator[asyncio.AbstractEventLoop, Any, Any]:
    loop = asyncio.get_event_loop_policy().get_event_loop()
    yield loop
    # loop.close()


@pytest.fixture(scope="session", autouse=True)
async def prepare_db(request: Any):
    settings.timescale_dbname += "-test"
    settings.mongo_dbname += "-test"
    await drop_postgres_db()
    await create_postgres_db()
    await drop_mongodb()

    # it seems that session is not closed in app
    # def finalizer():
    #     asyncio.get_event_loop().run_until_complete(drop_postgres_db())
    #
    # request.addfinalizer(finalizer)


@pytest.fixture(scope="session")
async def app(prepare_db) -> AsyncGenerator[FastAPI, Any]:
    async with LifespanManager(fastapi_app):
        yield fastapi_app


@pytest.fixture(scope="session")
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://testserver") as c:
        yield c


@pytest.fixture(scope="session")
def admin_user(app: FastAPI) -> User:
    return register_admin(user_id="admin")


@pytest.fixture(scope="session")
def admin_jwt(admin_user: User) -> str:
    token = create_jwt_token(
        user_id=admin_user.user_id,
        app_name="brickserver_frontend",
    )
    print(token)
    return token


@pytest.fixture(scope="function")
def admin_headers(admin_jwt: str):
    headers = {"Authorization": "Bearer " + admin_jwt}
    return headers


@pytest.fixture(scope="session")
def graphdb(app: FastAPI) -> GraphDB:
    return GraphDB(
        host=settings.graphdb_host,
        port=settings.graphdb_port,
        repository=settings.graphdb_repository,
    )


@pytest.fixture(scope="session")
async def domain(graphdb, client, admin_jwt) -> Domain:
    admin_headers = {"Authorization": "Bearer " + admin_jwt}
    resp = await client.post(
        f"{DOMAIN_BASE}/{TEST_DOMAIN_NAME}",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    await ensure_graphdb_brick_schema(graphdb, TEST_DOMAIN_NAME)
    data = resp.json()
    yield Domain(**data)
