from flask import Flask
from flask_injector import FlaskInjector

from .apis import blueprint

app = Flask(__name__)
app.register_blueprint(blueprint, url_prefix='/api/v1')


def configure_binding(binder):
    dbname = 'brick'
    user = 'bricker'
    pw = 'brick-demo'
    host = 'localhost'
    port = 6001
    from brick_data.timeseries import BrickTimeseries
    from brick_data.sparql import BrickSparql
    brick_ts = BrickTimeseries(dbname, user, pw, host, port)
    binder.bind(BrickTimeseries, to=brick_ts)
    brick_sparql = BrickSparql('http://localhost:8890/sparql', '1.0.3')
    binder.bind(BrickSparql, to=brick_sparql)


def create_app():
    FlaskInjector(app=app, modules=[configure_binding])
    return app

