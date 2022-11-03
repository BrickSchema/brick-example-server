from typing import Callable, Dict, Tuple, Union

from fastapi import Body, Depends, status
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
    query_domain,
)
from brick_server.minimal.interfaces import BaseTimeseries, RealActuation
from brick_server.minimal.schemas import Domain, IsSuccess

actuation_router = InferringRouter(tags=["Actuation"])


@cbv(actuation_router)
class ActuationEntity:
    actuation_iface: RealActuation = Depends(get_actuation_iface)
    ts_db: BaseTimeseries = Depends(get_ts_db)
    auth_logic: Callable = Depends(dependency_supplier.auth_logic)

    @actuation_router.post(
        "/",
        description="Actuate an entity to a value. Body format {{entity_id: [actuation_value, optional playceholder}, ...}",
        response_model=IsSuccess,
        status_code=200,
    )
    async def post(
        self,
        request: Request,
        domain: Domain = Depends(query_domain),
        # entity_id: str = Query(..., description=Descriptions.entity_id),
        actuation_request: Dict[str, Union[Tuple[str], Tuple[str, str]]] = Body(
            ...,
        ),
        token: HTTPAuthorizationCredentials = jwt_security_scheme,
    ) -> IsSuccess:
        # if scheduled_time:
        #    # TODO: Implement this
        #    raise exceptions.NotImplemented('Currently only immediate actuation is supported.')

        # actuation_key = actuation_request.key
        # actuation_value = actuation_request.key
        for entity_id, actuation in actuation_request.items():
            try:
                if len(actuation) == 2:
                    print(actuation[1])
                result, detail = self.actuation_iface.actuate(entity_id, actuation[0])
                return IsSuccess(is_success=result, reason=detail)
            except Exception as e:
                return IsSuccess(is_success=False, reason=f"{e}")

        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This should not be reached.")

    def relinquish(self, entity_id):
        pass
