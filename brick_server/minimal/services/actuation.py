from typing import Callable

from fastapi import Body, Depends, Query, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette.requests import Request

from brick_server.minimal.auth.authorization import jwt_security_scheme
from brick_server.minimal.dependencies import (
    dependency_supplier,
    get_actuation_iface,
    get_ts_db,
)
from brick_server.minimal.descriptions import Descriptions
from brick_server.minimal.interfaces import BaseTimeseries, RealActuation
from brick_server.minimal.schemas import ActuationRequest, IsSuccess

actuation_router = InferringRouter(tags=["Actuation"])


@cbv(actuation_router)
class ActuationEntity:
    actuation_iface: RealActuation = Depends(get_actuation_iface)
    ts_db: BaseTimeseries = Depends(get_ts_db)
    auth_logic: Callable = Depends(dependency_supplier.auth_logic)

    @actuation_router.post(
        "/",
        description="Actuate an entity to a value",
        response_model=IsSuccess,
        status_code=200,
    )
    async def post(
        self,
        request: Request,
        entity_id: str = Query(..., description=Descriptions.entity_id),
        actuation_request: ActuationRequest = Body(...),
        token: HTTPAuthorizationCredentials = jwt_security_scheme,
    ) -> IsSuccess:
        # if scheduled_time:
        #    # TODO: Implement this
        #    raise exceptions.NotImplemented('Currently only immediate actuation is supported.')

        actuation_value = actuation_request.value

        try:
            result, detail = self.actuation_iface.actuate(entity_id, actuation_value)
            return IsSuccess(is_success=result, reason=detail)
        except Exception as e:
            return IsSuccess(is_success=False, reason=f"{e}")

        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This should not be reached.")

    def relinquish(self, entity_id):
        pass
