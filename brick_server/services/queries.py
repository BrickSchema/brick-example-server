from pdb import set_trace as bp
from typing import Callable
import calendar
from datetime import datetime
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
from .models import sql_desc, sparql_desc
from ..dbs import BrickSparqlAsync
from ..helpers import striding_windows

from ..auth.authorization import authorized, auth_scheme
from ..models import get_all_relationships
from ..configs import configs
from ..dependencies import get_brick_db, get_ts_db, dependency_supplier
from ..interfaces import BaseTimeseries


query_router = InferringRouter('raw_queries')


@cbv(query_router)
class TimeseriesQuery():
    ts_db: BaseTimeseries = Depends(get_ts_db)
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)

    @query_router.post('/timeseries',
                      description='Raw PostgreSQL query for timeseries. (May not be exposed in the production deployment.)',
                      #response_model = TimeseriesData,
                      tags=['Raw Queries'],
                      )
    @authorized
    async def post(self,
                   request: Request,
                   query: str = Body(...,
                                     media_type='application/sql',
                                     description=sql_desc,
                                     ),
                   token: HTTPAuthorizationCredentials = Security(auth_scheme),
                   ):
        res = await self.ts_db.raw_query(query)
        formatted = format_raw_query(res)
        return formatted


def timeformatter(val):
    if isinstance(val, datetime):
        return calendar.timegm(val.timetuple())
    else:
        return val

def format_raw_query(res):
    return [tuple(timeformatter(row) for row in rows) for rows in res]

@cbv(query_router)
class SparqlQuery():
    brick_db: BrickSparqlAsync = Depends(get_brick_db)
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)

    @query_router.post('/sparql',
                       description='Raw SPARQL for Brick metadata. (May not be exposed in the production deployment.',
                       tags=['Raw Queries'],
                       )
    @authorized
    async def post(self,
                   #request: Request,
                   query: str = Body(...,
                                     media_type='application/sparql-query',
                                     description='sparql_desc'
                                     ),
                   token: HTTPAuthorizationCredentials = Security(auth_scheme),
                   ) -> SparqlResult:
        raw_res = await self.brick_db.query(query)
        return raw_res
