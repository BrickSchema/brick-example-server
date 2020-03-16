import pdb
from copy import deepcopy
from uuid import uuid4 as gen_uuid
from io import StringIO
import asyncio
from typing import ByteString, Any, Dict, Callable

import arrow
import rdflib
from rdflib import URIRef
from fastapi_utils.cbv import cbv
from fastapi import Depends, Header, HTTPException, Body, APIRouter, Query, Path
from fastapi_utils.inferring_router import InferringRouter
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request

from .models import TimeseriesData, ValueTypes, ValueType, IsSuccess, jwt_security_scheme
from .models import entity_id_desc, graph_desc, relationships_desc, start_time_desc, end_time_desc
from .models import value_type_desc, timeseries_data_desc
from ..helpers import striding_windows

from ..auth.authorization import authorized, O
from ..models import get_all_relationships
from ..configs import configs
from ..dependencies import get_brick_db, get_ts_db, dependency_supplier
from ..interfaces import BaseTimeseries



data_router = InferringRouter('data')


@cbv(data_router)
class TimeseriesById:
    ts_db: BaseTimeseries = Depends(get_ts_db)
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)

    @data_router.get('/timeseries/{entity_id}',
                     status_code=200,
                     #description='Get data of an entity with in a time range.',
                     response_model=TimeseriesData,
                     tags=['Data'],
                     )
    @authorized
    async def get(self,
                  request: Request,
                  entity_id: str = Path(..., description=entity_id_desc,),
                  start_time: float = Query(default=None, description=start_time_desc),
                  end_time: float = Query(default=None, description=end_time_desc),
                  value_types: ValueTypes = Query(default=[ValueType.number],
                                                  description=value_type_desc,
                                                  ),
                  token: HTTPAuthorizationCredentials = jwt_security_scheme,
                  ) -> TimeseriesData:
        value_types = [row.value for row in value_types]
        data = await self.ts_db.query([entity_id], start_time, end_time, value_types)
        columns= ['uuid', 'timestamp'] + value_types
        return TimeseriesData(data=data, columns=columns)

    @data_router.delete('/timeseries/{entity_id}',
                        status_code=200,
                        description='Delete data of an entity with in a time range or all the data if a time range is not given.',
                        response_model=IsSuccess,
                        tags=['Data'],
                        )
    @authorized
    async def delete(self,
                     request: Request,
                     entity_id: str = Path(..., description=entity_id_desc),
                     start_time: float = Query(default=None, description=start_time_desc),
                     end_time: float = Query(None, description=end_time_desc),
                     token: HTTPAuthorizationCredentials = jwt_security_scheme,
                     ) -> IsSuccess:
        await self.ts_db.delete([entity_id], start_time, end_time)
        return IsSuccess()


@cbv(data_router)
class Timeseries():
    ts_db: BaseTimeseries = Depends(get_ts_db)
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)

    @data_router.post('/timeseries',
                      status_code=200,
                      description='Post data. If fields are not given, default values are assumed.',
                      response_model=IsSuccess,
                      tags=['Data'],
                      )
    @authorized
    async def post(self,
                   request: Request,
                   data: TimeseriesData = Body(...,
                                               description=timeseries_data_desc,
                                               ),
                   token: HTTPAuthorizationCredentials = jwt_security_scheme,
                   ) -> IsSuccess:
        raw_data = data.data
        fields = data.columns
        unrecognized_fields = [field for field in fields
                               if field not in self.ts_db.value_cols + ['uuid', 'timestamp']]
        if unrecognized_fields:
            raise HTTPException(
                status_code=400,
                detail='There is an unrecognized field type: {0}'.format(unrecognized_fields),
            )
        uuid_idx = fields.index('uuid')
        timestamp_idx = fields.index('timestamp')
        futures = []
        for value_col in self.ts_db.value_cols:
            if value_col not in fields:
                continue
            value_idx = fields.index(value_col)
            data = [[datum[uuid_idx], datum[timestamp_idx], datum[value_idx]]
                    for datum in raw_data]
            futures = self.ts_db.add_data(data, data_type=value_col)
        await asyncio.gather(futures)
        return IsSuccess()
