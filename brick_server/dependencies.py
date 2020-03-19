from typing import Callable

from .dbs import lock_manager, brick_sparql, ts_db, actuation_iface
from .auth.authorization import check_admin, validate_token


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
