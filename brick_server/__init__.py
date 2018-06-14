import pdb
import json

from flask import Flask
from flask_injector import FlaskInjector
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

from .apis import blueprint, entity_api

configs = json.load(open('configs/configs.json'))
API_V1_PREFIX = '/api/v1'

def configure_binding(binder):
    from brick_data.timeseries import BrickTimeseries
    from brick_data.sparql import BrickSparql
    from brick_server.extensions.lockmanager import LockManager
    brick_ts_configs = configs['timeseries']
    brick_ts = BrickTimeseries(brick_ts_configs['dbname'],
                               brick_ts_configs['user'],
                               brick_ts_configs['password'],
                               brick_ts_configs['host'],
                               brick_ts_configs['port'],
                               )
    lockmanager_configs = configs['lockmanager']
    lock_manager = LockManager(lockmanager_configs['host'],
                               lockmanager_configs['port'],
                               lockmanager_configs['dbname'],
                               lockmanager_configs['user'],
                               lockmanager_configs['password'],
                               )
    brick_configs = configs['brick']
    base_ns = 'http://{hostname}{api_prefix}{entity_api_prefix}/'.format(
        hostname = configs['server']['hostname'],
        api_prefix = API_V1_PREFIX,
        entity_api_prefix = entity_api.path
    )
    brick_sparql = BrickSparql(brick_configs['host'],
                               brick_configs['brick_version'],
                               #base_ns=brick_configs['base_ns'],
                               base_ns=base_ns,
                               load_schema=True,
                               )
    binder.bind(BrickTimeseries, to=brick_ts)
    binder.bind(BrickSparql, to=brick_sparql)
    binder.bind(LockManager, to=lock_manager)

def create_app(**kwargs):
    app = Flask(__name__)
    app.register_blueprint(blueprint, url_prefix=API_V1_PREFIX)
    FlaskInjector(app=app, modules=[configure_binding])
    return app
