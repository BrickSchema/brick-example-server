from typing import Callable

from brick_server.minimal.dbs import brick_sparql, ts_db, actuation_iface, grafana_endpoint, lock_manager
from brick_server.minimal.auth.authorization import validate_token


class DependencySupplier(object):
    auth_logic: Callable

    def get_auth_logic(self):
        return self.auth_logic


dependency_supplier = DependencySupplier()
dependency_supplier.auth_logic = validate_token


def update_dependency_supplier(dep, obj):
    global dependency_supplier
    assert getattr(dependency_supplier, dep)
    setattr(dependency_supplier, dep, obj)


def get_brick_db():
    return brick_sparql


def get_lock_manager():
    return lock_manager


def get_ts_db():
    return ts_db


def get_actuation_iface():
    return actuation_iface


def get_grafana():
    return grafana_endpoint
