from datetime import datetime

from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from loguru import logger

from brick_server.minimal.interfaces.timeseries.base_timeseries import BaseTimeseries


class InfluxDBTimeseries(BaseTimeseries):
    def __init__(self, url, token, org, bucket):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = None

    async def init(self):
        self.client = InfluxDBClientAsync(url=self.url, token=self.token, org=self.org)
        ready = await self.client.ping()
        logger.info("InfluxDB Initialized: {}", ready)

    async def query(self, domain, entity_ids, start_time, end_time, limit=0, offset=0):
        query_api = self.client.query_api()
        # |> range(start: -10m)
        qstr = f'from(bucket:"{self.bucket}")'
        if start_time:
            qstr += f"\n|> range(start: {datetime.fromtimestamp(start_time)})"
        else:
            qstr += "\n|> range(start: -10m)"
        if end_time:
            qstr += f"\n|> range(stop: {datetime.fromtimestamp(end_time)})"
        if limit > 0:
            qstr += f"\n|> limit(n: {limit}, offset: {offset})"
        qstr += f'\n|> filter(fn: (r) => r._measurement == "heattransfer-test1" and r.id == "{entity_ids[0]}")'
        logger.info(qstr)

        records = await query_api.query_stream(qstr)
        data = []
        async for record in records:
            data.append([record["id"], record["_time"], record["_value"]])
            # print(record)
        return data


# token = 'y6CgzC9W3smC-RlBPFenYtByZz_kMVxcZ2-KwYc5ZJN08HuyZx52n5lVfKUA2RDBu1z55_M7Oav9UxHcWCR6fw=='
