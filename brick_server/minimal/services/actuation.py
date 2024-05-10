import asyncio
from typing import Any, Dict, Tuple, Union

import arrow
from fastapi import APIRouter, Body, Depends
from fastapi_restful.cbv import cbv
from starlette.requests import Request

from brick_server.minimal import models, schemas
from brick_server.minimal.interfaces import ActuationInterface, BaseTimeseries, GraphDB
from brick_server.minimal.securities.checker import PermissionCheckerActuation
from brick_server.minimal.utilities.dependencies import (
    get_actuation_iface,
    get_graphdb,
    get_jwt_payload,
    get_path_domain,
    get_ts_db,
)

router = APIRouter(prefix="/actuation", tags=["actuation"])


@cbv(router)
class ActuationEntity:
    actuation_iface: ActuationInterface = Depends(get_actuation_iface)
    ts_db: BaseTimeseries = Depends(get_ts_db)
    graphdb: GraphDB = Depends(get_graphdb)

    # TODO: use a better method to guard the playground api
    async def guard_before_actuation(
        self, domain, entity_id, value
    ) -> Tuple[bool, str, float, float]:
        pass

    async def actuate_entity(self, domain, jwt_payload, entity_id, actuation_payload):
        policy_time = 0
        guard_time = 0
        driver_time = 0
        actuation_time = 0
        try:
            (
                success,
                detail,
                policy_time,
                guard_time,
            ) = await self.guard_before_actuation(
                domain, entity_id, actuation_payload[0]
            )
            if not success:
                return (
                    success,
                    detail,
                    (policy_time, guard_time, driver_time, actuation_time),
                )
            if len(actuation_payload) == 2:
                print(actuation_payload[1])
            (
                success,
                detail,
                driver_time,
                actuation_time,
            ) = await self.actuation_iface.actuate(
                domain, entity_id, actuation_payload[0]
            )
            await self.ts_db.add_history_data(
                domain.name,
                entity_id,
                jwt_payload["sub"],
                jwt_payload["app_name"],
                jwt_payload.get("domain_user_app", ""),
                arrow.now(),
                actuation_payload[0],
            )
            return (
                success,
                detail,
                (policy_time, guard_time, driver_time, actuation_time),
            )
        except Exception as e:
            return False, f"{e}", (policy_time, guard_time, driver_time, actuation_time)

    @router.post(
        "/domains/{domain}",
        description="Actuate an entity to a value. Body format {{entity_id: [actuation_value, optional playceholder}, ...}",
        dependencies=[
            Depends(
                PermissionCheckerActuation(permission_type=schemas.PermissionType.WRITE)
            )
        ],
    )
    async def post(
        self,
        request: Request,
        domain: models.Domain = Depends(get_path_domain),
        actuation_request: Dict[str, Union[Tuple[str], Tuple[str, str]]] = Body(...),
        jwt_payload: Dict[str, Any] = Depends(get_jwt_payload),
    ) -> schemas.StandardResponse[schemas.ActuationResults]:
        # if scheduled_time:
        #    # TODO: Implement this
        #    raise exceptions.NotImplemented('Currently only immediate actuation is supported.')

        # actuation_key = actuation_request.key
        # actuation_value = actuation_request.key

        tasks = [
            self.actuate_entity(domain, jwt_payload, entity_id, actuation_payload)
            for entity_id, actuation_payload in actuation_request.items()
        ]
        task_results = await asyncio.gather(*tasks)
        results = []
        response_time = {"policy": 0, "guard": 0, "driver": 0, "actuation": 0}

        for (
            success,
            detail,
            (policy_time, guard_time, driver_time, actuation_time),
        ) in task_results:
            results.append(schemas.ActuationResult(success=success, detail=detail))
            response_time["policy"] += 1000 * policy_time
            response_time["guard"] += 1000 * guard_time
            response_time["driver"] += 1000 * driver_time
            response_time["actuation"] += 1000 * actuation_time

        # timer: _TimingStats = getattr(request.state, TIMER_ATTRIBUTE)
        # timer.take_split()

        return schemas.ActuationResults(
            results=results, response_time=response_time
        ).to_response()

        # for entity_id, actuation in actuation_request.items():
        #     if not await self.guard_before_actuation(domain, entity_id):
        #         continue
        #     await self.ts_db.add_history_data(
        #         domain.name,
        #         entity_id,
        #         jwt_payload["user_id"],
        #         jwt_payload["app_name"],
        #         jwt_payload.get("domain_user_app", ""),
        #         arrow.now(),
        #         actuation[0],
        #     )
        #
        # # return schemas.IsSuccess()
        #
        # for entity_id, actuation in actuation_request.items():
        #     try:
        #         if len(actuation) == 2:
        #             print(actuation[1])
        #         result, detail = self.actuation_iface.actuate(entity_id, actuation[0])
        #         return schemas.IsSuccess(is_success=result, reason=detail)
        #     except Exception as e:
        #         return schemas.IsSuccess(is_success=False, reason=f"{e}")
        #
        # raise HTTPException(status.HTTP_400_BAD_REQUEST, "This should not be reached.")
