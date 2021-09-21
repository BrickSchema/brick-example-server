import asyncio
from typing import Any, Callable

from fastapi import Body, Depends, HTTPException, Path, Query
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from brick_server.minimal.auth.authorization import (
    PermissionCheckerWithEntityId,
    R,
    W,
    authorized_arg,
)
from brick_server.minimal.dependencies import dependency_supplier, get_ts_db
from brick_server.minimal.descriptions import Descriptions
from brick_server.minimal.interfaces import BaseTimeseries
from brick_server.minimal.schemas import (
    IsSuccess,
    TimeseriesData,
    ValueType,
    ValueTypes,
    jwt_security_scheme,
)

data_router = InferringRouter(prefix="/data", tags=["Data"])


@cbv(data_router)
class TimeseriesById:
    ts_db: BaseTimeseries = Depends(get_ts_db)
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)

    @data_router.get(
        "/timeseries/{entity_id}",
        status_code=200,
        # description='Get data of an entity with in a time range.',
        response_model=TimeseriesData,
    )
    @authorized_arg(R)
    async def get(
        self,
        entity_id: str = Path(
            ...,
            description=Descriptions.entity_id,
        ),
        start_time: float = Query(default=None, description=Descriptions.start_time),
        end_time: float = Query(default=None, description=Descriptions.end_time),
        value_types: ValueTypes = Query(
            default=[ValueType.number],
            description=Descriptions.value_type,
        ),
        token: HTTPAuthorizationCredentials = jwt_security_scheme,
    ) -> TimeseriesData:
        value_types = [row.value for row in value_types]
        data = await self.ts_db.query([entity_id], start_time, end_time, value_types)
        columns = ["uuid", "timestamp"] + value_types
        return TimeseriesData(data=data, columns=columns)

    @data_router.delete(
        "/timeseries/{entity_id}",
        status_code=200,
        description="Delete data of an entity with in a time range or all the data if a time range is not given.",
        response_model=IsSuccess,
    )
    # @authorized_arg(W)
    async def delete(
        self,
        entity_id: str = Path(..., description=Descriptions.entity_id),
        start_time: float = Query(default=None, description=Descriptions.start_time),
        end_time: float = Query(None, description=Descriptions.end_time),
        token: HTTPAuthorizationCredentials = jwt_security_scheme,
        checker: Any = Depends(PermissionCheckerWithEntityId("write")),
    ) -> IsSuccess:
        # self.auth_logic(entity_id, "write")
        await self.ts_db.delete([entity_id], start_time, end_time)
        return IsSuccess()


def _get_entity_ids_ts_post(*args, **kwargs):
    rows = kwargs["data"].data
    columns = kwargs["data"].columns
    uuid_idx = columns.index("uuid")
    uuids = {row[uuid_idx] for row in rows}
    return uuids


@cbv(data_router)
class Timeseries:
    ts_db: BaseTimeseries = Depends(get_ts_db)
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)

    @data_router.post(
        "/timeseries",
        status_code=200,
        description="Post data. If fields are not given, default values are assumed.",
        response_model=IsSuccess,
    )
    @authorized_arg(W, _get_entity_ids_ts_post)
    async def post(
        self,
        data: TimeseriesData = Body(
            ...,
            description=Descriptions.timeseries_data,
        ),
        token: HTTPAuthorizationCredentials = jwt_security_scheme,
    ) -> IsSuccess:
        raw_data = data.data
        fields = data.columns
        unrecognized_fields = [
            field
            for field in fields
            if field not in self.ts_db.value_cols + ["uuid", "timestamp"]
        ]
        if unrecognized_fields:
            raise HTTPException(
                status_code=400,
                detail="There is an unrecognized field type: {}".format(
                    unrecognized_fields
                ),
            )
        uuid_idx = fields.index("uuid")
        timestamp_idx = fields.index("timestamp")
        futures = []
        for value_col in self.ts_db.value_cols:
            if value_col not in fields:
                continue
            value_idx = fields.index(value_col)
            data = [
                [datum[uuid_idx], datum[timestamp_idx], datum[value_idx]]
                for datum in raw_data
            ]
            futures = self.ts_db.add_data(data, data_type=value_col)
        await asyncio.gather(futures)
        return IsSuccess()