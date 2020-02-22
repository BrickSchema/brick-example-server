import pdb
from copy import deepcopy
from uuid import uuid4 as gen_uuid
from io import StringIO
import asyncio
from typing import ByteString, Any, Dict

import arrow
import rdflib
from rdflib import URIRef
from fastapi_utils.cbv import cbv
from fastapi import Depends, Header, HTTPException, Body, APIRouter, Query, Path, Security
from fastapi_utils.inferring_router import InferringRouter
from starlette.requests import Request
from fastapi.security import HTTPAuthorizationCredentials

from .models import TimeseriesData, SparqlResult
from ..dbs import BrickSparqlAsync
from ..helpers import striding_windows

from ..auth.authorization import authorized_admin, authorized, auth_scheme
from ..models import get_all_relationships
from ..configs import configs
from ..dbs import get_brick_db, get_ts_db
from ..interfaces import BaseTimeseries


query_router = InferringRouter('raw_queries')


@cbv(query_router)
class TimeseriesQuery():
    ts_db: BaseTimeseries = Depends(get_ts_db)

    @query_router.get('/timeseries',
                      description='Raw PostgreSQL query for timeseries. (May not be exposed in the production deployment.)',
                      response_model = TimeseriesData,
                      tags=['Raw Queries'],
                      )
    @authorized_admin
    async def get(self,
                  query: str = Body(..., media_type='application/sql'),
                  token: HTTPAuthorizationCredentials = Security(auth_scheme),
                  ):
        res = await self.ts_db.raw_query(query)
        data = [[row[0], arrow.get(row[1]).timestamp, row[2]] for row in res]
        res = {
            'data': data,
            'fields': ['uuid', 'timestamp', 'value']
        }
        return res, 200

@cbv(query_router)
class SparqlQuery():
    brick_db: BaseTimeseries = Depends(get_brick_db)


    @query_router.post('/sparql',
                       description='Raw SPARQL for Brick metadata. (May not be exposed in the production deployment.',
                       tags=['Raw Queries'],
                       )
    @authorized_admin
    async def post(self,
                   query: str = Body(..., media_type='application/sparql-query'),
                   token: HTTPAuthorizationCredentials = Security(auth_scheme),
                   ) -> SparqlResult:
        raw_res = await self.brick_db.query(query)
        return raw_res
