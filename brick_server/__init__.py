import pdb
from .services.data.resources import TimeseriesById
from .services.data.resources import Timeseries

from flask import Flask
from flask_injector import FlaskInjector
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

from .apis import blueprint

def configure_binding(binder):
    dbname = 'brick'
    user = 'bricker'
    pw = 'brick-demo'
    host = 'localhost'
    port = 6001
    from brick_data.timeseries import BrickTimeseries
    from brick_data.sparql import BrickSparql
    from brick_server.extensions.lockmanager import LockManager
    lock_manager = LockManager(host, port, dbname, user, pw)
    brick_ts = BrickTimeseries(dbname, user, pw, host, port)
    brick_sparql = BrickSparql('http://localhost:8890/sparql', '1.0.3',
                               base_ns='http://jason.com/')
    binder.bind(BrickTimeseries, to=brick_ts)
    binder.bind(BrickSparql, to=brick_sparql)
    binder.bind(LockManager, to=lock_manager)

def create_app():
    app = Flask(__name__)
    app.register_blueprint(blueprint, url_prefix='/api/v1')
    FlaskInjector(app=app, modules=[configure_binding])

    spec = APISpec(
        title='Brick Server',
        version='1.0.0',
        openapi_version='3.0',
        plugins=[
            FlaskPlugin(),
            MarshmallowPlugin(),
        ],
    )


    return app
