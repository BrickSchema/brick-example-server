import pdb
import json

from flask import Flask
from flask_injector import FlaskInjector
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

from .apis import blueprint

def configure_binding(binder):
    configs = json.load(open('configs/configs.json'))
    dbname = 'brick'
    user = 'bricker'
    pw = 'brick-demo'
    host = 'localhost'
    port = 6001
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
    brick_sparql = BrickSparql(brick_configs['host'],
                               brick_configs['brick_version'],
                               base_ns=brick_configs['base_ns'],
                               )
    binder.bind(BrickTimeseries, to=brick_ts)
    binder.bind(BrickSparql, to=brick_sparql)
    binder.bind(LockManager, to=lock_manager)

def create_app():
    app = Flask(__name__)
    app.register_blueprint(blueprint, url_prefix='/api/v1')
    FlaskInjector(app=app, modules=[configure_binding])
    return app
