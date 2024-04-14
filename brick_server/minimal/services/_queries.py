import calendar
from datetime import datetime
from typing import Any, Callable

from fastapi import Body, Depends
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter
from starlette.requests import Request

from brick_server.minimal.auth.checker import PermissionChecker, PermissionType
from brick_server.minimal.dependencies import (
    dependency_supplier,
    get_graphdb,
    get_ts_db,
    path_domain,
)
from brick_server.minimal.interfaces import BaseTimeseries, GraphDB
from brick_server.minimal.schemas import Domain, SparqlResult
from brick_server.minimal.utilities.descriptions import Descriptions

query_router = InferringRouter(tags=["Raw Queries"])


@cbv(query_router)
class TimeseriesQuery:
    ts_db: BaseTimeseries = Depends(get_ts_db)
    auth_logic: Callable = Depends(dependency_supplier.auth_logic)

    @query_router.post(
        "/timeseries",
        description="Raw PostgreSQL query for timeseries. (May not be exposed in the production deployment.)",
        # response_model = TimeseriesData,
    )
    async def post(
        self,
        request: Request,
        # domain: Domain = Depends(query_domain),
        query: str = Body(
            ...,
            media_type="application/sql",
            description=Descriptions.sql,
        ),
        checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
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
    auth_logic: Callable = Depends(dependency_supplier.auth_logic)
    graphdb: GraphDB = Depends(get_graphdb)

    @query_router.post(
        "/domains/{domain}/sparql",
        description="Raw SPARQL for Brick metadata. (May not be exposed in the production deployment.",
    )
    async def post(
        self,
        # request: Request,
        domain: Domain = Depends(path_domain),
        query: str = Body(
            ..., media_type="application/sparql-query", description=Descriptions.sparql
        ),
        checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
    ) -> SparqlResult:
        raw_res = await self.graphdb.query(domain.name, query)
        return raw_res
