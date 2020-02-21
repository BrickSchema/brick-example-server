import os
import asyncio
import pdb
import json

import redis

#from brick_data.timeseries import BrickTimeseries
from brick_data.sparql import BrickSparqlAsync
from brick_data.common import TS_DB, BRICK_DB
from brick_data.queryprocessor.querysynthesizer import TimescaledbSynthesizer
from brick_server.extensions.lockmanager import LockManager

from .configs import configs
from .interfaces import DummyActuation, BrickTimeseries, AsyncpgTimeseries

#
brick_ts_configs = configs['timeseries']
#brick_ts = BrickTimeseries(brick_ts_configs['dbname'],
#                           brick_ts_configs['user'],
#                           brick_ts_configs['password'],
#                           brick_ts_configs['host'],
#                           brick_ts_configs['port'],
#                           )
lockmanager_configs = configs['lockmanager']
lock_manager = LockManager(lockmanager_configs['host'],
                           lockmanager_configs['port'],
                           lockmanager_configs['dbname'],
                           lockmanager_configs['user'],
                           lockmanager_configs['password'],
                           )

brick_configs = configs['brick']
#if configs['server']['use_hostname_as_ns']:
#    base_ns = 'http://{hostname}{api_prefix}{entity_api_prefix}/'.format(
#        hostname = configs['server']['hostname'],
#        api_prefix = API_V1_PREFIX,
#        entity_api_prefix = entity_api.path
#    )
#else:
#brick_sparql = BrickSparql(brick_configs['host'],
#                           brick_configs['brick_version'],
#                           graph=brick_configs['base_graph'],
#                           base_ns=base_ns,
#                           load_schema=True,
#                           )
#for prefix, ns in brick_configs['building_nss'].items():
#    brick_sparql.add_ns_prefix(ns, prefix)
#brick_sparql.add_ns_prefix(brick_configs['user_ns'], 'user')
#
#synthesizers = {
#    BRICK_DB: BrickSynthesizer(),
#    TS_DB: TimescaledbSynthesizer(),
#}
#dbs = {
#    BRICK_DB: brick_sparql,
#    TS_DB: brick_ts,
#    #STRUCT_DB: struct_db,
#}
#
actuation_iface = DummyActuation()

base_ns = brick_configs['base_ns']
brick_sparql = BrickSparqlAsync(brick_configs['host'],
                                brick_configs['brick_version'],
                                graph=brick_configs['base_graph'],
                                base_ns=base_ns,
                                )
asyncio.ensure_future(brick_sparql.load_schema())

ts_db = AsyncpgTimeseries(brick_ts_configs['dbname'],
                          brick_ts_configs['user'],
                          brick_ts_configs['password'],
                          brick_ts_configs['host'],
                          brick_ts_configs['port'],
                          )
asyncio.ensure_future(ts_db.init())

def get_brick_db():
    return brick_sparql

def get_lock_manager():
    return lock_manager

def get_ts_db():
    return ts_db

def get_actuation_iface():
    return actuation_iface
