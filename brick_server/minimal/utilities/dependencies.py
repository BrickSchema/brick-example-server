from typing import Any, Callable

from bson import ObjectId
from fastapi import Path, Query, Request

from brick_server.minimal import models
from brick_server.minimal.interfaces.actuation import actuation_iface
from brick_server.minimal.interfaces.graphdb import GraphDB, graphdb
from brick_server.minimal.interfaces.mongodb import AsyncDatabase, async_db
from brick_server.minimal.interfaces.timeseries import (
    AsyncpgTimeseries,
    InfluxDBTimeseries,
    influx_db,
    timeseries_iface,
    ts_db,
)
from brick_server.minimal.schemas import PaginationQuery
from brick_server.minimal.schemas.base import PaginationLimit
from brick_server.minimal.utilities.exceptions import BizError, ErrorCode


class DependencySupplier:
    # TODO: move it
    # from brick_server.minimal.auth.authorization import PermissionType
    # auth_logic_func_type = Callable[[Set[str], PermissionType], bool]
    # auth_logic: Callable[[], auth_logic_func_type]
    auth_logic: Callable[[], Any]

    # def get_auth_logic(self) -> Callable[[Set[str], PermissionType], bool]:
    #     return self.auth_logic


dependency_supplier = DependencySupplier()
dependency_supplier.auth_logic = None


def update_dependency_supplier(func: Callable[[], Any]):
    dependency_supplier.auth_logic = func


def get_auth_logic():
    return dependency_supplier.auth_logic


def get_graphdb() -> GraphDB:
    return graphdb


def get_ts_db() -> AsyncpgTimeseries:
    return ts_db


def get_influx_db() -> InfluxDBTimeseries:
    return influx_db


def get_mongodb() -> AsyncDatabase:
    return async_db


def get_actuation_iface():
    return actuation_iface


def get_timeseries_iface():
    return timeseries_iface


def get_pagination_query(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0, le=PaginationLimit),
) -> PaginationQuery:
    return PaginationQuery(offset=offset, limit=limit)


async def _get_domain(domain: str) -> models.Domain:
    if ObjectId.is_valid(domain):
        domain_model = await models.Domain.get(domain)
    else:
        domain_model = await models.Domain.find_one(models.Domain.name == domain)
    return domain_model


async def get_path_domain_optional(request: Request) -> models.Domain | None:
    domain = request.path_params.get("domain", None)
    if domain is None:
        return None
    return await _get_domain(str(domain))


async def get_path_domain(domain: str = Path(...)) -> models.Domain:
    domain_model = await _get_domain(domain)
    if domain_model is None:
        raise BizError(ErrorCode.DomainNotFoundError)
    return domain_model


async def get_path_user(user: str = Path(...)) -> models.User:
    if ObjectId.is_valid(user):
        user_model = await models.User.get(user)
    else:
        user_model = await models.User.find_one(models.User.name == user)
    if user_model is None:
        raise BizError(ErrorCode.UserNotFoundError)
    return user_model
