from typing import Callable

from fastapi import APIRouter, Body, Depends
from fastapi_restful.cbv import cbv

from brick_server.minimal import models, schemas
from brick_server.minimal.interfaces import GraphDB
from brick_server.minimal.securities.checker import PermissionChecker
from brick_server.minimal.utilities.dependencies import (
    dependency_supplier,
    get_graphdb,
    get_path_domain,
)
from brick_server.minimal.utilities.descriptions import Descriptions

router = APIRouter(tags=["queries"])


# @cbv(query_router)
# class TimeseriesQuery:
#     ts_db: BaseTimeseries = Depends(get_ts_db)
#     auth_logic: Callable = Depends(dependency_supplier.auth_logic)
#
#     @query_router.post(
#         "/timeseries",
#         description="Raw PostgreSQL query for timeseries. (May not be exposed in the production deployment.)",
#         # response_model = TimeseriesData,
#     )
#     async def post(
#         self,
#         request: Request,
#         # domain: Domain = Depends(query_domain),
#         query: str = Body(
#             ...,
#             media_type="application/sql",
#             description=Descriptions.sql,
#         ),
#         checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
#     ):
#         res = await self.ts_db.raw_query(query)
#         formatted = format_raw_query(res)
#         return formatted
#
#
# def timeformatter(val):
#     if isinstance(val, datetime):
#         return calendar.timegm(val.timetuple())
#     else:
#         return val
#
#
# def format_raw_query(res):
#     return [tuple(timeformatter(row) for row in rows) for rows in res]
#


@cbv(router)
class SparqlQuery:
    auth_logic: Callable = Depends(dependency_supplier.auth_logic)
    graphdb: GraphDB = Depends(get_graphdb)

    @router.post(
        "/domains/{domain}/sparql",
        description="Raw SPARQL for Brick metadata. (May not be exposed in the production deployment.",
        dependencies=[
            Depends(PermissionChecker(permission_scope=schemas.PermissionScope.DOMAIN))
        ],
    )
    async def post(
        self,
        # request: Request,
        domain: models.Domain = Depends(get_path_domain),
        query: str = Body(
            ..., media_type="application/sparql-query", description=Descriptions.sparql
        ),
    ) -> schemas.StandardResponse[dict]:
        raw_result, prefixes = await self.graphdb.query(domain.name, query)
        result = self.graphdb.parse_result(raw_result, prefixes)
        return schemas.StandardResponse(result)
