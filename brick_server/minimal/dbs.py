import os
from pdb import set_trace as bp
import asyncio
import pdb
import json

import redis
from mongoengine import connect as mongo_connect

# from brick_data.timeseries import BrickTimeseries
from brick_data.sparql import BrickSparqlAsync, BrickSparql
from brick_data.common import TS_DB, BRICK_DB
from brick_data.queryprocessor.querysynthesizer import TimescaledbSynthesizer
from brick_server.minimal.extensions.lockmanager import LockManager
import asyncpg
from fastapi_rest_framework.config import settings

# from .configs import configs
from .interfaces import DummyActuation, BrickTimeseries, AsyncpgTimeseries
from .interfaces.grafana import GrafanaEndpoint

mongo_connection = mongo_connect(
    host=settings.mongo_host,
    port=settings.mongo_port,
    username=settings.mongo_username,
    password=settings.mongo_password,
    db=settings.mongo_dbname,
    connect=False,
)

# lockmanager_configs = configs["lockmanager"]
lock_manager = LockManager(
    settings.lockmanager_host,
    settings.lockmanager_port,
    settings.lockmanager_dbname,
    settings.lockmanager_username,
    settings.lockmanager_password,
)

actuation_iface = DummyActuation()

# brick_configs = configs["brick"]
brick_url = (
    f"http://{settings.brick_host}:{settings.brick_port}/{settings.brick_api_endpoint}"
)

brick_sparql = BrickSparqlAsync(
    brick_url,
    settings.brick_version,
    graph=settings.brick_base_graph,
    base_ns=settings.brick_base_ns,
)

brick_sparql_sync = BrickSparql(
    brick_url,
    settings.brick_version,
    graph=settings.brick_base_graph,
    base_ns=settings.brick_base_ns,
)


# brick_ts_configs = configs["timeseries"]
ts_db = AsyncpgTimeseries(
    settings.timescale_dbname,
    settings.timescale_username,
    settings.timescale_password,
    settings.timescale_host,
    settings.timescale_port,
)
try:
    asyncio.ensure_future(ts_db.init())
except asyncpg.exceptions.DuplicateTableError:
    print("Timescale tabels have been already created.")

grafana_url = f"http://{settings.grafana_host}:{settings.grafana_port}/{settings.grafana_api_endpoint}"
grafana_endpoint = GrafanaEndpoint(grafana_url, settings.grafana_api_key)
