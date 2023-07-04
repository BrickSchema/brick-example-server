from typing import Any, Callable, Dict, Tuple, Union

import arrow
from fastapi import Body, Depends, status
from fastapi.exceptions import HTTPException
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette.requests import Request

from brick_server.minimal import models, schemas
from brick_server.minimal.dependencies import (
    dependency_supplier,
    get_actuation_iface,
    get_jwt_payload,
    get_ts_db,
    path_domain,
)
from brick_server.minimal.interfaces import ActuationInterface, BaseTimeseries

actuation_router = InferringRouter(tags=["Actuation"])


@cbv(actuation_router)
class ActuationEntity:
    actuation_iface: ActuationInterface = Depends(get_actuation_iface)
    ts_db: BaseTimeseries = Depends(get_ts_db)
    auth_logic: Callable = Depends(dependency_supplier.auth_logic)

    @actuation_router.post(
        "/domains/{domain}",
        description="Actuate an entity to a value. Body format {{entity_id: [actuation_value, optional playceholder}, ...}",
        response_model=schemas.IsSuccess,
        status_code=200,
    )
    async def post(
        self,
        request: Request,
        domain: models.Domain = Depends(path_domain),
        # entity_id: str = Query(..., description=Descriptions.entity_id),
        actuation_request: Dict[str, Union[Tuple[str], Tuple[str, str]]] = Body(
            ...,
        ),
        jwt_payload: Dict[str, Any] = Depends(get_jwt_payload),
    ) -> schemas.IsSuccess:
        # if scheduled_time:
        #    # TODO: Implement this
        #    raise exceptions.NotImplemented('Currently only immediate actuation is supported.')

        # actuation_key = actuation_request.key
        # actuation_value = actuation_request.key

        for entity_id, actuation in actuation_request.items():
            await self.ts_db.add_history_data(
                domain.name,
                entity_id,
                jwt_payload["user_id"],
                jwt_payload["app_name"],
                jwt_payload.get("domain_user_app", ""),
                arrow.now(),
                actuation[0],
            )

        # return schemas.IsSuccess()

        for entity_id, actuation in actuation_request.items():
            try:
                if len(actuation) == 2:
                    print(actuation[1])
                result, detail = self.actuation_iface.actuate(entity_id, actuation[0])
                return schemas.IsSuccess(is_success=result, reason=detail)
            except Exception as e:
                return schemas.IsSuccess(is_success=False, reason=f"{e}")

        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This should not be reached.")

    def relinquish(self, entity_id):
        pass
