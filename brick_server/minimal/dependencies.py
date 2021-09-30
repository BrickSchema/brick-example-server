from typing import Any, Callable, Dict, Set

from fastapi.security import HTTPAuthorizationCredentials

from brick_server.minimal.auth.authorization import (
    PermissionType,
    default_auth_logic,
    jwt_security_scheme,
    parse_jwt_token,
)
from brick_server.minimal.dbs import (
    actuation_iface,
    brick_sparql,
    grafana_endpoint,
    ts_db,
)
from brick_server.minimal.interfaces import AsyncpgTimeseries

auth_logic_func_type = Callable[[Set[str], PermissionType], bool]


class DependencySupplier(object):
    auth_logic: Callable[[], auth_logic_func_type]

    # def get_auth_logic(self) -> Callable[[Set[str], PermissionType], bool]:
    #     return self.auth_logic


dependency_supplier = DependencySupplier()
dependency_supplier.auth_logic = default_auth_logic


def update_dependency_supplier(func: Callable[[], auth_logic_func_type]):
    dependency_supplier.auth_logic = func


def get_brick_db():
    return brick_sparql


def get_ts_db() -> AsyncpgTimeseries:
    return ts_db


def get_actuation_iface():
    return actuation_iface


def get_grafana():
    return grafana_endpoint


def get_jwt_payload(
    token: HTTPAuthorizationCredentials = jwt_security_scheme,
) -> Dict[str, Any]:
    return parse_jwt_token(token.credentials)
