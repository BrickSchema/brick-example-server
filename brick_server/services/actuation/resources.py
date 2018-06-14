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

from brick_data.sparql import BrickSparql
from brick_data.timeseries import BrickTimeseries

from .models import reqparser, actuate_api
from brick_server.extensions.lockmanager import LockManager

@actuate_api.route('/<string:entity_id>', methods=['post'])
class ActuationEntity(Resource):
    @inject
    def __init__(self,
                 brick_sparql: BrickSparql,
                 ts_db: BrickTimeseries,
                 lock_manager: LockManager,
                 api):
        self.brick_sparql = brick_sparql
        self.ts_db = ts_db
        self.lock_manager = lock_manager
        super(ActuationEntity, self).__init__(api)

    @actuate_api.doc(description='Actuate an entity to a value')
    @actuate_api.response(200, 'Sucess')
    @actuate_api.param('entity_id', 'The ID of an entity for the data request.', _in='url')
    @actuate_api.param('value', 'An actuation value in float.', type=float, _in='body')
    @actuate_api.param('relinquish', 'Relinquish.', type=bool, _in='body')
    def post(self, entity_id):
        # TODO
        # - read paramterrs
        # - start a session
        # - get a lock of the resource
        # - actuation
        # - verify the actuation
        # - post the updated value to the timeseries database
        # - close the session - abort the session if anything goes wrong.
        args = reqparser.parse_args()
        actuation_value = args.value
        scheduled_time = args.get('scheduled_time', None)
        if scheduled_time:
            # TODO: Implement this
            raise exceptions.NotImplemented('Currently only immediate actuation is implemented.')

        with self.lock_manager.advisory_lock(entity_id) as lock_acquired:
            assert lock_acquired, exceptions.BadRequest('Lock for {0} cannot be acquired'.format(entity_id))
            self.actuation(entity_id, actuation_value)
            actuated_time = arrow.get()
            data = [[entity_id, actuated_time.timestamp, actuation_value]]
            self.ts_db.add_data(data)
            return None

        raise exceptions.InternalServerError('This should not be reached.')

    def relinquish(self, entity_id):
        pass

    def actuation(self, entity_id, value):
        # TODO: Implement relevant scripts.
        #       For now, actuation is assumed to be done in certain time.
        random_delay = random.uniform(0, 5)
        time.sleep(random_delay)
        print('{0} is actuated as {1}'.format(entity_id, value))
        return True
