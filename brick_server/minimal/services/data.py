import asyncio
from typing import Any, Callable

from fastapi import Body, Depends, HTTPException, Query, status
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from loguru import logger

from brick_server.minimal.auth.authorization import (
    PermissionCheckerWithData,
    PermissionCheckerWithEntityId,
    PermissionType,
)
from brick_server.minimal.dependencies import dependency_supplier, get_ts_db
from brick_server.minimal.descriptions import Descriptions
from brick_server.minimal.interfaces import AsyncpgTimeseries
from brick_server.minimal.schemas import (
    IsSuccess,
    TimeseriesData,
    ValueType,
    ValueTypes,
)

data_router = InferringRouter(tags=["Data"])


@cbv(data_router)
class Timeseries:
    ts_db: AsyncpgTimeseries = Depends(get_ts_db)
    auth_logic: Callable = Depends(dependency_supplier.auth_logic)

    @data_router.get(
        "/timeseries",
        status_code=200,
        # description='Get data of an entity with in a time range.',
        response_model=TimeseriesData,
    )
    async def get(
        self,
        entity_id: str = Query(
            ...,
            description=Descriptions.entity_id,
        ),
        start_time: float = Query(default=None, description=Descriptions.start_time),
        end_time: float = Query(default=None, description=Descriptions.end_time),
        value_types: ValueTypes = Query(
            default=[ValueType.number],
            description=Descriptions.value_type,
        ),
        checker: Any = Depends(PermissionCheckerWithEntityId(PermissionType.read)),
    ) -> TimeseriesData:
        value_types = [row.value for row in value_types]
        data = await self.ts_db.query([entity_id], start_time, end_time, value_types)
        columns = ["uuid", "timestamp"] + value_types
        return TimeseriesData(data=data, columns=columns)

    @data_router.delete(
        "/timeseries",
        status_code=200,
        description="Delete data of an entity with in a time range or all the data if a time range is not given.",
        response_model=IsSuccess,
    )
    async def delete(
        self,
        entity_id: str = Query(..., description=Descriptions.entity_id),
        start_time: float = Query(default=None, description=Descriptions.start_time),
        end_time: float = Query(None, description=Descriptions.end_time),
        checker: Any = Depends(PermissionCheckerWithEntityId(PermissionType.write)),
    ) -> IsSuccess:
        # self.auth_logic(entity_id, "write")
        await self.ts_db.delete([entity_id], start_time, end_time)
        return IsSuccess()

    @data_router.post(
        "/timeseries",
        status_code=200,
        description="Post data. If fields are not given, default values are assumed.",
        response_model=IsSuccess,
    )
    async def post(
        self,
        data: TimeseriesData = Body(
            ...,
            description=Descriptions.timeseries_data,
        ),
        checker: Any = Depends(PermissionCheckerWithData(PermissionType.write)),
    ) -> IsSuccess:
        raw_data = data.data
        if not raw_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Empty data posted"
            )
        fields = data.columns
        unrecognized_fields = [
            field
            for field in fields
            if field not in self.ts_db.value_cols + ["uuid", "timestamp"]
        ]
        if unrecognized_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
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
            data = []
            for datum in raw_data:
                try:
                    data.append(
                        [datum[uuid_idx], datum[timestamp_idx], float(datum[value_idx])]
                    )
                except Exception as e:
                    logger.info(f"data {datum} with error {e}")
            futures = self.add_data(data, data_type=value_col)
        await asyncio.gather(futures)
        return IsSuccess()

    async def add_data(self, data, data_type):
        try:
            await self.ts_db.add_data(data, data_type=data_type)
        except Exception as e:
            logger.exception(e)
