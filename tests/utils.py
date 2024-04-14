import arrow
import asyncpg
from mongoengine import connect as mongo_connect
from tenacity import retry, stop_after_delay, wait_exponential

from brick_server.minimal.config.manager import settings
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
        settings.TIMESCALE_DATABASE,
    )
    conn = await get_postgres_conn()
    await conn.execute(f'DROP DATABASE IF EXISTS "{settings.TIMESCALE_DATABASE}"')
    await conn.close()


async def create_postgres_db():
    print(
        "create test db",
        settings.timescale_host,
        settings.timescale_port,
        settings.TIMESCALE_DATABASE,
    )
    conn = await get_postgres_conn()
    await conn.execute(
        f'CREATE DATABASE "{settings.TIMESCALE_DATABASE}" OWNER "{settings.timescale_username}"'
    )
    await conn.close()
    conn = await get_postgres_conn(database=settings.TIMESCALE_DATABASE)
    await conn.execute("CREATE EXTENSION IF NOT EXISTS postgis CASCADE")
    await conn.close()


async def drop_mongodb():
    print(
        "drop test mongodb",
        settings.mongo_host,
        settings.mongo_port,
        settings.mongo_dbname,
    )
    db = mongo_connect(
        host=settings.mongo_host,
        port=settings.mongo_port,
        username=settings.mongo_username,
        password=settings.mongo_password,
        db=settings.mongo_dbname,
        connect=False,
    )
    db.drop_database(settings.mongo_dbname)


@retry(stop=stop_after_delay(600), wait=wait_exponential(multiplier=1, max=32))
async def ensure_graphdb_upload(graphdb: GraphDB, repository: str, name: str) -> None:
    result = await graphdb.check_import_schema(repository, name)
    assert result


@retry(stop=stop_after_delay(600), wait=wait_exponential(multiplier=1, max=32))
async def ensure_graphdb_brick_schema(graphdb: GraphDB, repository: str) -> None:
    graphs = await graphdb.list_graphs(repository)
    assert settings.default_brick_url in graphs
