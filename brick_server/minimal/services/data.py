import asyncio
from typing import Any, Callable

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi_restful.cbv import cbv
from loguru import logger

from brick_server.minimal import models, schemas
from brick_server.minimal.interfaces import TimeseriesInterface
from brick_server.minimal.securities.checker import (
    PermissionCheckerWithData,
    PermissionCheckerWithEntityId,
    PermissionType,
)
from brick_server.minimal.utilities.dependencies import (
    dependency_supplier,
    get_pagination_query,
    get_path_domain,
    get_timeseries_iface,
)
from brick_server.minimal.utilities.descriptions import Descriptions

router = APIRouter(prefix="/data", tags=["data"])


@cbv(router)
class Timeseries:
    ts_db: TimeseriesInterface = Depends(get_timeseries_iface)
    auth_logic: Callable = Depends(dependency_supplier.auth_logic)

    @router.get(
        "/timeseries/domains/{domain}",
        status_code=200,
        # description='Get data of an entity with in a time range.',
    )
    async def get(
        self,
        domain: models.Domain = Depends(get_path_domain),
        entity_id: str = Query(
            ...,
            description=Descriptions.entity_id,
        ),
        start_time: float = Query(default=None, description=Descriptions.start_time),
        end_time: float = Query(default=None, description=Descriptions.end_time),
        value_types: list[schemas.ValueType] = Query(
            default=[schemas.ValueType.number],
            description=Descriptions.value_type,
        ),
        pagination: schemas.PaginationQuery = Depends(get_pagination_query),
        # checker: Any = Depends(PermissionCheckerWithEntityId(PermissionType.READ)),
    ) -> schemas.StandardResponse[schemas.TimeseriesData]:
        value_types = [row.value for row in value_types]
        data = await self.ts_db.query(
            domain,
            [entity_id],
            start_time,
            end_time,
            # value_types,
            pagination.limit,
            pagination.offset,
        )
        columns = ["uuid", "timestamp"] + value_types
        return schemas.TimeseriesData(data=data, columns=columns).to_response()

    @router.delete(
        "/timeseries/domains/{domain}",
        status_code=200,
        description="Delete data of an entity with in a time range or all the data if a time range is not given.",
    )
    async def delete(
        self,
        domain: models.Domain = Depends(get_path_domain),
        entity_id: str = Query(..., description=Descriptions.entity_id),
        start_time: float = Query(default=None, description=Descriptions.start_time),
        end_time: float = Query(None, description=Descriptions.end_time),
        checker: Any = Depends(PermissionCheckerWithEntityId(PermissionType.WRITE)),
    ) -> schemas.StandardResponse[schemas.Empty]:
        # self.auth_logic(entity_id, "write")
        await self.ts_db.delete(domain.name, [entity_id], start_time, end_time)
        return schemas.StandardResponse()

    @router.post(
        "/timeseries/domains/{domain}",
        status_code=200,
        description="Post data. If fields are not given, default values are assumed.",
    )
    async def post(
        self,
        domain: models.Domain = Depends(get_path_domain),
        data: schemas.TimeseriesData = Body(
            ...,
            description=Descriptions.timeseries_data,
        ),
        checker: Any = Depends(PermissionCheckerWithData(PermissionType.WRITE)),
    ) -> schemas.StandardResponse[schemas.Empty]:
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
            futures = self.add_data(domain.name, data, data_type=value_col)
        await asyncio.gather(futures)
        return schemas.StandardResponse()

    async def add_data(self, domain_name, data, data_type):
        try:
            await self.ts_db.add_data(domain_name, data, data_type=data_type)
        except Exception as e:
            logger.exception(e)
