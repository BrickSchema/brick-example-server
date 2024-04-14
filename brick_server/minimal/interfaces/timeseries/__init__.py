from loguru import logger

from brick_server.minimal.config.manager import settings
from brick_server.minimal.interfaces.timeseries.asyncpg import AsyncpgTimeseries
from brick_server.minimal.interfaces.timeseries.base_timeseries import BaseTimeseries
from brick_server.minimal.interfaces.timeseries.influxdb import InfluxDBTimeseries
from brick_server.minimal.interfaces.timeseries.timeseries_interface import (
    TimeseriesInterface,
)

ts_db = AsyncpgTimeseries(
    settings.TIMESCALE_DATABASE,
    settings.TIMESCALE_USERNAME,
    settings.TIMESCALE_PASSWORD,
    settings.TIMESCALE_HOST,
    settings.TIMESCALE_PORT,
)

influx_db = InfluxDBTimeseries(
    settings.INFLUXDB_URL,
    settings.INFLUXDB_TOKEN,
    settings.INFLUXDB_ORG,
    settings.INFLUXDB_BUCKET,
)

timeseries_iface = TimeseriesInterface()


async def initialize_timeseries():
    logger.info("Init timescale tables")
    await ts_db.init()
    logger.info("Init InfluxDB")
    await influx_db.init()


async def dispose_timeseries():
    logger.info("Dispose timescale connection")
    await ts_db.dispose()
