import os
from pdb import set_trace as bp
import asyncio
import pdb
import json

import redis
from mongoengine import connect as mongo_connect

#from brick_data.timeseries import BrickTimeseries
from brick_data.sparql import BrickSparqlAsync, BrickSparql
from brick_data.common import TS_DB, BRICK_DB
from brick_data.queryprocessor.querysynthesizer import TimescaledbSynthesizer
from brick_server.extensions.lockmanager import LockManager
import asyncpg

from .configs import configs
from .interfaces import DummyActuation, BrickTimeseries, AsyncpgTimeseries


lockmanager_configs = configs['lockmanager']
lock_manager = LockManager(lockmanager_configs['host'],
                           lockmanager_configs['port'],
                           lockmanager_configs['dbname'],
                           lockmanager_configs['user'],
                           lockmanager_configs['password'],
                           )

actuation_iface = DummyActuation()

brick_configs = configs['brick']
brick_sparql = BrickSparqlAsync(brick_configs['host'],
                                brick_configs['brick_version'],
                                graph=brick_configs['base_graph'],
                                base_ns=brick_configs['base_ns']
                                )

brick_sparql_sync = BrickSparql(brick_configs['host'],
                                brick_configs['brick_version'],
                                graph=brick_configs['base_graph'],
                                base_ns=brick_configs['base_ns']
                                )

asyncio.ensure_future(brick_sparql.load_schema())

brick_ts_configs = configs['timeseries']
ts_db = AsyncpgTimeseries(brick_ts_configs['dbname'],
                          brick_ts_configs['user'],
                          brick_ts_configs['password'],
                          brick_ts_configs['host'],
                          brick_ts_configs['port'],
                          )
try:
    asyncio.ensure_future(ts_db.init())
except asyncpg.exceptions.DuplicateTableError:
    print('Timescale tabels have been already created.')
