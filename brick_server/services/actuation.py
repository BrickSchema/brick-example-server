import pdb
from contextlib import contextmanager
import random
import time

import arrow
import timeout_decorator
from timeout_decorator import TimeoutError
from flask import request
from injector import inject
from flask_restplus import Resource
from werkzeug import exceptions

from fastapi_utils.cbv import cbv
from fastapi import Depends, Header, HTTPException, Body, Query, Path
from fastapi_utils.inferring_router import InferringRouter
from fastapi.security import HTTPAuthorizationCredentials


from .models import IsSuccess, ActuationRequest, jwt_security_scheme
from ..dbs import get_ts_db, get_lock_manager, get_actuation_iface
from brick_server.extensions.lockmanager import LockManager
from ..auth.authorization import authorized_admin, auth_scheme
from ..interfaces import BaseActuation, BaseTimeseries
from ..configs import configs


actuation_router = InferringRouter('actuation')


@cbv(actuation_router)
class ActuationEntity(Resource):
    lock_manager: LockManager = Depends(get_lock_manager)
    actuation_iface: BaseActuation = Depends(get_actuation_iface)
    ts_db: BaseTimeseries = Depends(get_ts_db)

    @actuation_router.post('/{entity_id}',
                           description='Actuate an entity to a value',
                           response_model=IsSuccess,
                           status_code=200,
                           tags=['Actuation'],
                           )
    @authorized_admin
    async def post(self,
                   entity_id: str = Path(None),
                   actuation_request: ActuationRequest = Body(None),
                   token: HTTPAuthorizationCredentials = jwt_security_scheme,
                   ) -> IsSuccess:
        #if scheduled_time:
        #    # TODO: Implement this
        #    raise exceptions.NotImplemented('Currently only immediate actuation is supported.')

        actuation_value = actuation_request.value
        with self.lock_manager.advisory_lock(entity_id) as lock_acquired:
            assert lock_acquired, exceptions.BadRequest('Lock for {0} cannot be acquired'.format(entity_id))
            self.actuation_iface.actuate(entity_id, actuation_value)
            actuated_time = arrow.get()
            data = [[entity_id, actuated_time.timestamp, actuation_value]]
            await self.ts_db.add_data(data)
            return IsSuccess()

        raise exceptions.InternalServerError('This should not be reached.')

    def relinquish(self, entity_id):
        pass
