from typing import Callable

from fastapi import Body, Depends, Path
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette.requests import Request
from werkzeug import exceptions

from brick_server.extensions.lockmanager import LockManager

from ..auth.authorization import authorized
from ..dependencies import (
    dependency_supplier,
    get_actuation_iface,
    get_lock_manager,
    get_ts_db,
)
from ..interfaces import BaseTimeseries, RealActuation
from .models import ActuationRequest, IsSuccess, jwt_security_scheme

actuation_router = InferringRouter(prefix="/actuation")


@cbv(actuation_router)
class ActuationEntity:
    lock_manager: LockManager = Depends(get_lock_manager)
    actuation_iface: RealActuation = Depends(get_actuation_iface)
    ts_db: BaseTimeseries = Depends(get_ts_db)
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)

    @actuation_router.post(
        "/{entity_id:path}",
        description="Actuate an entity to a value",
        response_model=IsSuccess,
        status_code=200,
        tags=["Actuation"],
    )
    @authorized
    async def post(
        self,
        request: Request,
        entity_id: str = Path(...),
        actuation_request: ActuationRequest = Body(...),
        token: HTTPAuthorizationCredentials = jwt_security_scheme,
    ) -> IsSuccess:
        # if scheduled_time:
        #    # TODO: Implement this
        #    raise exceptions.NotImplemented('Currently only immediate actuation is supported.')

        actuation_value = actuation_request.value
        # with self.lock_manager.advisory_lock(entity_id) as lock_acquired:
        #     assert lock_acquired, exceptions.BadRequest('Lock for {0} cannot be acquired'.format(entity_id))
        #     self.actuation_iface.actuate(entity_id, actuation_value)
        #     actuated_time = arrow.get()
        #     data = [[entity_id, actuated_time.timestamp, actuation_value]]
        #     await self.ts_db.add_data(data)
        #     return IsSuccess()
        try:
            status, detail = self.actuation_iface.actuate(entity_id, actuation_value)
            return IsSuccess(is_success=status, reason=detail)
        except Exception as e:
            return IsSuccess(is_success=False, reason=f"{e}")

        raise exceptions.InternalServerError("This should not be reached.")

    def relinquish(self, entity_id):
        pass
