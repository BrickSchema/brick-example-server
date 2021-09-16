import calendar
from datetime import datetime
from typing import Callable

from fastapi import Body, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette.requests import Request

from brick_server.minimal.auth.authorization import auth_scheme, authorized
from brick_server.minimal.dbs import BrickSparqlAsync
from brick_server.minimal.dependencies import (
    dependency_supplier,
    get_brick_db,
    get_ts_db,
)
from brick_server.minimal.descriptions import Descriptions
from brick_server.minimal.interfaces import BaseTimeseries
from brick_server.minimal.schemas import SparqlResult

query_router = InferringRouter(prefix="/raw_queries")


@cbv(query_router)
class TimeseriesQuery:
    ts_db: BaseTimeseries = Depends(get_ts_db)
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)

    @query_router.post(
        "/timeseries",
        description="Raw PostgreSQL query for timeseries. (May not be exposed in the production deployment.)",
        # response_model = TimeseriesData,
        tags=["Raw Queries"],
    )
    @authorized
    async def post(
        self,
        request: Request,
        query: str = Body(
            ...,
            media_type="application/sql",
            description=Descriptions.sql,
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
class SparqlQuery:
    brick_db: BrickSparqlAsync = Depends(get_brick_db)
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)

    @query_router.post(
        "/sparql",
        description="Raw SPARQL for Brick metadata. (May not be exposed in the production deployment.",
        tags=["Raw Queries"],
    )
    @authorized
    async def post(
        self,
        # request: Request,
        query: str = Body(
            ..., media_type="application/sparql-query", description=Descriptions.sparql
        ),
        token: HTTPAuthorizationCredentials = Security(auth_scheme),
    ) -> SparqlResult:
        raw_res = await self.brick_db.query(query)
        return raw_res
