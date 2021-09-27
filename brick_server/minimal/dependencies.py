from typing import Callable, Set

from brick_server.minimal.auth.authorization import PermissionType, default_auth_logic
from brick_server.minimal.dbs import (
    actuation_iface,
    brick_sparql,
    grafana_endpoint,
    ts_db,
)
from brick_server.minimal.interfaces import AsyncpgTimeseries


class DependencySupplier(object):
    auth_logic: Callable[[Set[str], PermissionType], bool]

    # def get_auth_logic(self) -> Callable[[Set[str], PermissionType], bool]:
    #     return self.auth_logic


dependency_supplier = DependencySupplier()
dependency_supplier.auth_logic = default_auth_logic


def update_dependency_supplier(func: Callable[[Set[str], PermissionType], bool]):
    dependency_supplier.auth_logic = func


def get_brick_db():
    return brick_sparql


def get_ts_db() -> AsyncpgTimeseries:
    return ts_db


def get_actuation_iface():
    return actuation_iface


def get_grafana():
    return grafana_endpoint
