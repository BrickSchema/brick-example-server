import pdb
from contextlib import contextmanager
import random
import time

import arrow
import timeout_decorator
from timeout_decorator import TimeoutError
from flask import request
from injector import inject
from flask_restplus import Namespace, Api, Resource
from werkzeug import exceptions

from brick_data.sparql import BrickSparql
from brick_data.timeseries import BrickTimeseries

from .models import reqparser, entity_api, entity_model
from brick_server.extensions.lockmanager import LockManager


def get_entity_type(db, entity_id):
    qstr = """
    select ?o where {{
    :{0} a ?o.
    }}
    """.format(entity_id)
    res = db.query(qstr)
    if res[1]:
        assert len(res[1]) == 1
        return res[1][0][0]
    else:
        raise Exception('Type not found')

def get_all_relationships(db, entity_id):
    qstr = """
    select ?p ?o where {{
    {{
    :{0} ?p ?o.
    FILTER NOT EXISTS {{ :{0} a ?o .}}
    }}
    UNION
    {{
    ?inverse_p owl:inverseOf ?p .
    ?o ?inverse_p :{0}.
    }}
    }}
    """.format(entity_id)
    res = db.query(qstr)
    return res[1]

@entity_api.route('/<string:entity_id>/actuate', methods=['post'])
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

    @entity_api.marshal_with(entity_model)
    @entity_api.response(200, 'Sucess', model=entity_model)
    @entity_api.response(401, 'Server Error')
    @entity_api.param('entity_id', 'The ID of an entity for the data request.')
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

@entity_api.route('/<string:entity_id>', methods=['get', 'delete'])
class EntityById(Resource):
    @inject
    def __init__(self, db: BrickSparql, api):
        self.db = db
        super(EntityById, self).__init__(api)

    @entity_api.marshal_with(entity_model)
    @entity_api.response(200, 'Sucess', model=entity_model)
    @entity_api.response(401, 'Server Error')
    @entity_api.param('entity_id', 'The ID of an entity for the data request.')
    def get(self, entity_id):
        entity_type = get_entity_type(self.db, entity_id)
        relationships = get_all_relationships(self.db, entity_id)
        res = {
            'type': entity_type,
            'relationships': relationships,
        }
        return res

    @entity_api.param('entity_id', 'The ID of an entity for the data request.')
    @entity_api.response(200, 'Sucess')
    def delete(self, entity_id):
        args = reqparser.parse_args()
        return None

    @entity_api.param('data', 'Data', _in='body')
    @entity_api.response(201, 'Success')
    def post(self, entity_id):
        args = reqparser.parse_args()
        data = args['data']
