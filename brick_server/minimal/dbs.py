from fastapi_rest_framework.config import settings
from mongoengine import connect as mongo_connect

from brick_server.minimal.interfaces import (
    ActuationInterface,
    AsyncpgTimeseries,
    InfluxDBTimeseries,
    TimeseriesInterface,
)
from brick_server.minimal.interfaces.grafana import GrafanaEndpoint
from brick_server.minimal.interfaces.graphdb import GraphDB

mongo_connection = mongo_connect(
    host=settings.mongo_host,
    port=settings.mongo_port,
    username=settings.mongo_username,
    password=settings.mongo_password,
    db=settings.mongo_dbname,
    connect=False,
)


actuation_iface = ActuationInterface()

# brick_configs = configs["brick"]
brick_url = (
    f"http://{settings.brick_host}:{settings.brick_port}/{settings.brick_api_endpoint}"
)

# brick_sparql = BrickSparqlAsync(
#     brick_url,
#     settings.brick_version,
#     graph=settings.brick_base_graph,
#     base_ns=settings.brick_base_ns,
# )
#
# brick_sparql_sync = BrickSparql(
#     brick_url,
#     settings.brick_version,
#     graph=settings.brick_base_graph,
#     base_ns=settings.brick_base_ns,
# )

graphdb = GraphDB(
    host=settings.graphdb_host,
    port=settings.graphdb_port,
    repository=settings.graphdb_repository,
)

# brick_ts_configs = configs["timeseries"]
ts_db = AsyncpgTimeseries(
    settings.timescale_dbname,
    settings.timescale_username,
    settings.timescale_password,
    settings.timescale_host,
    settings.timescale_port,
)

influx_db = InfluxDBTimeseries(
    settings.influxdb_url,
    settings.influxdb_token,
    settings.influxdb_org,
    settings.influxdb_bucket,
)
timeseries_iface = TimeseriesInterface()


grafana_url = f"http://{settings.grafana_host}:{settings.grafana_port}/{settings.grafana_api_endpoint}"
grafana_endpoint = GrafanaEndpoint(grafana_url, settings.grafana_api_key)
