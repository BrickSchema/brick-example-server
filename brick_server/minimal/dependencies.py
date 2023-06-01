from typing import Any, Callable, Dict

from fastapi import Path, Query
from fastapi.security import HTTPAuthorizationCredentials

from brick_server.minimal.auth.jwt import jwt_security_scheme, parse_jwt_token
from brick_server.minimal.interfaces import AsyncpgTimeseries, GraphDB
from brick_server.minimal.models import Domain, get_doc
from brick_server.minimal.schemas import NoneNegativeInt, Pagination, PaginationLimit


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


def get_ts_db() -> AsyncpgTimeseries:
    from brick_server.minimal.dbs import ts_db

    return ts_db


def get_graphdb() -> GraphDB:
    from brick_server.minimal.dbs import graphdb

    return graphdb


def get_actuation_iface():
    from brick_server.minimal.dbs import actuation_iface

    return actuation_iface


def get_grafana():
    from brick_server.minimal.dbs import grafana_endpoint

    return grafana_endpoint


def get_jwt_payload(
    token: HTTPAuthorizationCredentials = jwt_security_scheme,
) -> Dict[str, Any]:
    return parse_jwt_token(token.credentials)


def query_domain(domain: str = Query(...)) -> Domain:
    return get_doc(Domain, name=domain)


def path_domain(domain: str = Path(...)) -> Domain:
    return get_doc(Domain, name=domain)


def query_pagination(
    offset: NoneNegativeInt = Query(0), limit: PaginationLimit = Query(100)
) -> Pagination:
    return Pagination(offset=offset, limit=limit)
