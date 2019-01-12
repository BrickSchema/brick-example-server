import pdb
from contextlib import contextmanager

import arrow
import timeout_decorator
from timeout_decorator import TimeoutError
from flask import request
from injector import inject
from flask_restplus import Namespace, Api, Resource
from brick_data.sparql import BrickSparql

from .models import reqparser, entity_api, entity_model


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
    def __init__(self, db: BrickSparql, api):
        self.db = db
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
        with api.commit_or_abort(
                default_error_message="Failed to actuate {0}".format(entity_id)
        ):
            actuation()
            return team

    @contextmanager
    def lock_entity_actuation(self, entity_id):
        try:
            yield
        finally:
            pass


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
        self.db.add_data(data)
        return None, 201
