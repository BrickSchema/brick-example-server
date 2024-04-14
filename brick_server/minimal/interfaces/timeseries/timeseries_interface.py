from urllib.parse import urlparse

from loguru import logger

from brick_server.minimal.interfaces.timeseries.base_timeseries import BaseTimeseries
from brick_server.minimal.utilities.exceptions import BizError, ErrorCode
from brick_server.minimal.utilities.utils import get_external_references


class TimeseriesInterface:
    def __init__(self):
        from brick_server.minimal.interfaces.timeseries import influx_db, ts_db

        self.db_dict = {
            "psql": ts_db,
            "postgres": ts_db,
            "postgresql": ts_db,
            "influxdb": influx_db,
        }

    async def get_timeseries_driver(self, external_references) -> BaseTimeseries:
        types = external_references.getall(
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        )
        if "https://brickschema.org/schema/Brick/ref#TimeseriesReference" not in types:
            raise BizError(ErrorCode.TimeseriesDriverNotFoundError, ",".join(types))

        stored_at = external_references.get(
            "https://brickschema.org/schema/Brick/ref#storedAt"
        )
        # logger.info(stored_at)
        url = urlparse(stored_at)
        if url.scheme in self.db_dict:
            return self.db_dict[url.scheme]

        raise BizError(ErrorCode.TimeseriesDriverNotFoundError, url.scheme)

    async def query(self, domain, entity_ids, start_time, end_time, limit=0, offset=0):
        # TODO: support multiple entity ids
        entity_id = entity_ids[0]
        # TODO: get timeseries reference only
        external_references = await get_external_references(domain, entity_id)
        logger.info(external_references)
        driver = await self.get_timeseries_driver(external_references)
        timeseries_id = external_references.get(
            "https://brickschema.org/schema/Brick/ref#hasTimeseriesId"
        )
        return await driver.query(
            domain.name, [timeseries_id], start_time, end_time, limit, offset
        )
