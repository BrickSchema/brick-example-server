from datetime import datetime
from uuid import uuid4 as gen_uuid

import aiofiles
import asyncpg
import pandas as pd
from loguru import logger
from shapely.geometry import Point

from brick_server.minimal.interfaces.timeseries.base_timeseries import BaseTimeseries

POSTGRESQL_LOC = "ST_AsGeoJson(loc)"


def encode_loc_type(value_type):
    if value_type == "loc":
        return POSTGRESQL_LOC
    else:
        return value_type


def striding_windows(l, w_size):
    curr_idx = 0
    while curr_idx < len(l):
        yield l[curr_idx : curr_idx + w_size]
        curr_idx += w_size


class AsyncpgTimeseries(BaseTimeseries):
    def __init__(
        self,
        dbname,
        user,
        pw,
        host,
        port=5601,
        pool_config={},
        read_blob_configs={"dir": "./blobs"},
        read_blob=None,
        write_blob=None,
        *args,
        **kwargs,
    ):
        self.DB_NAME = dbname
        self.TABLE_NAME_PREFIX = "brick_data"
        self.HISTORY_TABLE_NAME_PREFIX = "brick_history"
        self.conn_str = f"postgres://{user}:{pw}@{host}:{port}/{dbname}"
        self.value_cols = ["number", "text", "loc"]
        self.pagination_size = 500

        self.read_blob_configs = read_blob_configs
        if not read_blob:
            self.read_blob = self.read_blob_fs
        if not write_blob:
            self.write_blob = self.write_blob_fs

        self.column_type_map = {
            "time": "TIMESTAMP",
            "number": "DOUBLE PRECISION",
            "text": "TEXT",
            "loc": "geometry(Point,4326)",
        }
        self.pool = None

    async def init(self, **pool_config):
        self.pool = await asyncpg.create_pool(dsn=self.conn_str, **pool_config)
        # await self._init_table()
        logger.info("Timeseries Initialized")

    def get_table_name(self, domain_name):
        return f"{self.TABLE_NAME_PREFIX}_{domain_name}"

    def get_history_table_name(self, domain_name):
        return f"{self.HISTORY_TABLE_NAME_PREFIX}_{domain_name}"

    async def init_table(self, domain_name):
        table_name = self.get_table_name(domain_name)
        qstrs = [
            """
            CREATE TABLE IF NOT EXISTS {table_name} (
                uuid TEXT NOT NULL,
                --time TIMESTAMP without time zone NOT NULL,
                time TIMESTAMP NOT NULL,
                number DOUBLE PRECISION,
                text TEXT,
                loc geometry(Point,4326),
                PRIMARY KEY (uuid, time)
            );
            """.format(
                table_name=table_name
            ),
            """
            CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
            """,
            """
            SELECT create_hypertable('{table_name}', 'time');
            """.format(
                table_name=table_name
            ),
            """
            CREATE INDEX IF NOT EXISTS brick_data_time_index ON {table_name} (time DESC);
            """.format(
                table_name=table_name
            ),
            """
            CREATE INDEX IF NOT EXISTS brick_data_uuid_index ON {table_name} (uuid);
            """.format(
                table_name=table_name
            ),
        ]
        async with self.pool.acquire() as conn:
            for qstr in qstrs:
                try:
                    res = await conn.execute(qstr)
                except Exception as e:
                    if "already a hypertable" in str(e):
                        pass
                    else:
                        raise e
        logger.info("Init table {}", table_name)

    async def init_history_table(self, domain_name):
        table_name = self.get_history_table_name(domain_name)
        qstrs = [
            """
            CREATE TABLE IF NOT EXISTS {table_name} (
                uuid TEXT NOT NULL,
                user_id TEXT NOT NULL,
                app_name TEXT NOT NULL,
                domain_user_app TEXT NOT NULL,
                time TIMESTAMP NOT NULL,
                value TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (uuid, time)
            );
            """.format(
                table_name=table_name
            ),
            """
                CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
            """,
            """
            SELECT create_hypertable('{table_name}', 'time');
            """.format(
                table_name=table_name
            ),
            """
            CREATE INDEX IF NOT EXISTS brick_history_time_index ON {table_name} (time DESC);
            """.format(
                table_name=table_name
            ),
            """
            CREATE INDEX IF NOT EXISTS brick_data_uuid_index ON {table_name} (uuid);
            """.format(
                table_name=table_name
            ),
        ]
        async with self.pool.acquire() as conn:
            for qstr in qstrs:
                try:
                    res = await conn.execute(qstr)
                except Exception as e:
                    if "already a hypertable" in str(e):
                        pass
                    else:
                        raise e
        logger.info("Init table {}", table_name)

    async def read_blob_fs(self, pointer):
        async with aiofiles.open(
            self.read_blob_configs["dir"] + "/" + pointer, mode="rb"
        ) as f:
            contents = await f.read()
        return contents

    async def write_blob_fs(self, data, pointer):
        async with aiofiles.open(
            self.read_blob_configs["dir"] + "/" + pointer, mode="wb"
        ) as f:
            await f.write(data)

    def display_data(self, res):
        times = []
        uuids = []
        numbers = []
        texts = []
        locs = []
        for row in res:
            [uuid, t, number, text, loc] = row
            times.append(t)
            uuids.append(uuid)
            numbers.append(number)
            texts.append(text)
            locs.append(loc)
        df = pd.DataFrame(
            {"time": times, "uuid": uuids, "number": numbers, "loc": locs}
        )
        print(df)

    def serialize_records(self, records):
        return [tuple(row) for row in records]

    async def get_all_data(self, domain_name, query=""):
        table_name = self.get_table_name(domain_name)
        return await self._fetch(
            """
                                 SELECT uuid, time, number, text, ST_AsGeoJson(loc)
                                 FROM {}
                                 """.format(
                table_name
            )
        )

    # def _format_select_res(self, res, return_type=None):
    #     if not return_type:
    #         pass
    #     elif return_type == 'sparql-like':
    #         var_begin = qstr.lower().index('select') + 6
    #         var_end = qstr.lower().index('from')
    #         var_names = qstr[var_begin:var_end].split()
    #         res = {
    #             'var_names': var_names,
    #             'tuples': res,
    #         }
    #     return res

    async def _fetch(self, qstr, *args, **kwargs):
        async with self.pool.acquire() as conn:
            return self.serialize_records(await conn.fetch(qstr, *args, **kwargs))

    async def _execute(self, qstr, *args, **kwargs):
        async with self.pool.acquire() as conn:
            return await conn.execute(qstr, *args, **kwargs)

    # async def _exec_query(self, qstr):
    #     await self._execute(qstr)
    #     query_type = cur.statusmessage.split()[0]
    #     if query_type =='SELECT':
    #         raw_res = cur.fetchall()
    #     elif query_type == 'DELETE':
    #         raw_res = None
    #     elif query_type == 'INSERT':
    #         raw_res = None
    #     else:
    #         raise Exception('not implemented yet')
    #     return raw_res

    def _timestamp2str(self, ts):
        # return datetime.fromtimestamp(ts, tz=pytz.utc)
        # TODO: Debug timezone
        return datetime.fromtimestamp(ts)

    async def raw_query(self, qstr, return_type=None):
        # raw_res = self._exec_query(qstr)
        # res = self._format_select_res(raw_res, return_type)
        res = await self._fetch(qstr)
        return res

    async def delete(self, domain_name, uuids, start_time=None, end_time=None):
        table_name = self.get_table_name(domain_name)
        assert uuids, "Any UUIDs should be given for deleting timeseries data"
        qstr = """
        DELETE FROM {}
        WHERE
        """.format(
            table_name
        )
        qstr += "uuid IN ({})\n AND ".format("'" + "', '".join(uuids) + "'")
        if start_time:
            qstr += "time >= '{}'\n AND ".format(self._timestamp2str(start_time))
        if end_time:
            qstr += "time < '{}'\n AND ".format(self._timestamp2str(end_time))
        qstr = qstr[:-4]
        res = await self._execute(qstr)
        return res

    def encode_value_types(self, value_types):
        return list(map(encode_loc_type, value_types))

    async def query(
        self,
        domain_name,
        uuids=[],
        start_time=None,
        end_time=None,
        limit=-1,
        offset=0,
        value_types=["number"],
    ):
        # qstr = """
        # SELECT uuid, time, number, text, ST_AsGeoJson(loc) FROM {0}
        # """.format(self.TABLE_NAME)
        table_name = self.get_table_name(domain_name)
        assert value_types
        qstr = """
        SELECT uuid, time, {value_types} FROM {table}
        """.format(
            value_types=", ".join(value_types), table=table_name
        )
        if not (start_time or end_time or uuids):
            qstr += "DUMY"  # dummy characters to be removed.
        else:
            qstr += "WHERE\n"
            if start_time:
                qstr += "time >= '{}'\n AND ".format(self._timestamp2str(start_time))
            if end_time:
                qstr += "time < '{}'\n AND ".format(self._timestamp2str(end_time))
            if uuids:
                qstr += "uuid IN ({})\n AND ".format("'" + "', '".join(uuids) + "'")
        qstr = qstr[:-4]
        qstr += "OFFSET {}\n".format(offset)
        if limit > 0:
            qstr += "LIMIT {}\n".format(limit)
        return await self._fetch(qstr)

    # TODO: Unify encode & add_data over different data types.

    def _encode_number_data(self, data):
        return [(datum[0], self._timestamp2str(datum[1]), datum[2]) for datum in data]

    def _encode_text_data(self, data):
        return [
            (datum[0], self._timestamp2str(datum[1]), str(datum[2])) for datum in data
        ]

    def _encode_loc_data(self, data):
        data = [
            (
                datum[0],
                self._timestamp2str(datum[1]),
                Point((datum[2][0], datum[2][1])).wkb_hex,
            )
            for datum in data
        ]
        return data

    async def _add_number_data(self, domain_name, data):
        encoded_data = self._encode_number_data(data)
        res = await self._bulk_upsert_data(domain_name, encoded_data, "number")

    async def _add_text_data(self, domain_name, data):
        encoded_data = self._encode_text_data(data)
        res = await self._bulk_upsert_data(domain_name, encoded_data, "text")

    async def _add_loc_data(self, domain_name, data):
        encoded_data = self._encode_loc_data(data)
        res = await self._bulk_upsert_data(domain_name, encoded_data, "text")

    async def _bulk_upsert_data(self, domain_name, data, col_name):
        table_name = self.get_table_name(domain_name)
        temp_table = "_temp_{}".format(gen_uuid().hex)
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
CREATE TEMPORARY TABLE {temp_table} (
uuid TEXT, time TIMESTAMP, {col_name} {data_type})
            """.format(
                    col_name=col_name,
                    temp_table=temp_table,
                    data_type=self.column_type_map[col_name],
                )
            )
            await conn.copy_records_to_table(temp_table, records=data)
            res = await conn.execute(
                """
INSERT INTO {target_table} (uuid, time, {col_name})
SELECT * FROM {temp_table}
ON CONFLICT (time, uuid)
DO UPDATE SET {col_name}=EXCLUDED.{col_name}
WHERE {target_table}.{col_name} <> EXCLUDED.{col_name};
DROP TABLE {temp_table};
            """.format(
                    target_table=table_name,
                    temp_table=temp_table,
                    col_name=col_name,
                )
            )

    async def add_data(self, domain_name, data, data_type="number"):
        """
        - input
            - uuid (str): a unique id of one sensor
            - data (list(tuple)): timeseries data. E.g., [(1055151, 70.0), 1055153, 70.1)]
        """
        assert data_type in self.value_cols  # TODO: Make these ENUM.

        if not data:
            raise Exception("Empty data to insert")
        if data_type == "number":
            await self._add_number_data(domain_name, data)
        elif data_type == "loc":
            await self._add_loc_data(domain_name, data)
        elif data_type == "text":
            await self._add_text_data(domain_name, data)

    async def add_history_data(
        self, domain_name, entity_id, user_id, app_name, domain_user_app, time, value
    ):
        table_name = self.get_history_table_name(domain_name)
        async with self.pool.acquire() as conn:
            res = await conn.execute(
                f"""INSERT INTO {table_name} (uuid, user_id, app_name, domain_user_app, time, value)
                VALUES ('{entity_id}', '{user_id}', '{app_name}', '{domain_user_app}', '{time}', '{value}');"""
            )

    async def get_history_data(self, domain_name, entity_ids):
        table_name = self.get_history_table_name(domain_name)
        entity_ids_string = ",".join(map(lambda x: f"'{x}'", entity_ids))
        query = f"""SELECT (uuid, user_id, app_name, domain_user_app, time, value) FROM {table_name} WHERE uuid IN ({entity_ids_string});"""
        logger.info(query)
        async with self.pool.acquire() as conn:
            res = [record["row"] for record in await conn.fetch(query)]
            logger.info(res)
            return res


def main():
    dbname = "brick"
    user = "bricker"
    pw = "brick-demo"
    host = "localhost"
    port = 6001
    brick_ts = AsyncpgTimeseries(dbname, user, pw, host, port)

    data = [
        ["id1", 1524436788, 70.0],
        ["id2", 1524436788, 900],
        ["id21", 1524437788, 70.5],
    ]
    brick_ts.add_data(data)

    loc_data = [
        ["id1", 1524436788, [0, 0]],
        ["id2", 1524436788, [0, 1]],
    ]
    brick_ts.add_data(loc_data, "loc")

    res = brick_ts.query()
    brick_ts.display_data(res)
    print(res)


if __name__ == "__main__":
    main()
