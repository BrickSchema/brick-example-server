import asyncio

import arrow
import asyncpg
from fastapi_rest_framework.config import settings

from brick_server.minimal.interfaces.graphdb import GraphDB
from brick_server.minimal.models import User


def register_admin(user_id: str) -> User:
    users = User.objects(user_id=user_id)
    if not users:
        user = User(
            user_id=user_id,
            name=user_id,
            is_admin=True,
            is_approved=True,
            registration_time=arrow.get().datetime,
            email=user_id,
            activated_apps=[],
        )
        user.save()
    else:
        user = users[0]
        user.is_admin = True
        user.save()
    return user


async def get_postgres_conn(database: str = "template1"):
    conn = await asyncpg.connect(
        host=settings.timescale_host,
        port=settings.timescale_port,
        user=settings.timescale_username,
        password=settings.timescale_password,
        database=database,
    )
    return conn


async def drop_postgres_db():
    print(
        "drop test db",
        settings.timescale_host,
        settings.timescale_port,
        settings.timescale_dbname,
    )
    conn = await get_postgres_conn()
    await conn.execute(f'DROP DATABASE IF EXISTS "{settings.timescale_dbname}"')
    await conn.close()


async def create_postgres_db():
    print(
        "create test db",
        settings.timescale_host,
        settings.timescale_port,
        settings.timescale_dbname,
    )
    conn = await get_postgres_conn()
    await conn.execute(
        f'CREATE DATABASE "{settings.timescale_dbname}" OWNER "{settings.timescale_username}"'
    )
    await conn.close()
    conn = await get_postgres_conn(database=settings.timescale_dbname)
    await conn.execute("CREATE EXTENSION IF NOT EXISTS postgis CASCADE")
    await conn.close()


async def ensure_graphdb_upload(graphdb: GraphDB, name: str) -> None:
    for i in range(7):
        try:
            result = await graphdb.check_schema(name)
            if result:
                return
        except Exception as e:
            print(e)
        await asyncio.sleep(2 ** i)

    assert False
