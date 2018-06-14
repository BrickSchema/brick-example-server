import pdb
from contextlib import contextmanager
import random
import time
from uuid import uuid4 as gen_uuid

import arrow
import timeout_decorator
from timeout_decorator import TimeoutError
from flask import request
from injector import inject
from flask_restplus import Resource
from flask_restplus.marshalling import marshal
from werkzeug import exceptions

from brick_data.sparql import BrickSparql
from brick_data.timeseries import BrickTimeseries

from .models import reqparser, entity_api, entity_model, entities_model
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


@entity_api.route('/<string:entity_id>', methods=['get', 'delete', 'post'], strict_slashes=False)
class EntityById(Resource):
    @inject
    def __init__(self, db: BrickSparql, api):
        self.db = db
        super(EntityById, self).__init__(api)

    @entity_api.doc(description='Get information about an entity including type and its relationships with others')
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

    @entity_api.doc(description='Delete an entity along with its relationships and data')
    @entity_api.param('entity_id', 'The ID of an entity for the data request.')
    @entity_api.response(200, 'Sucess')
    def delete(self, entity_id):
        raise exceptions.NotImplemented('TODO: Delete corresponding entity.')
        return None

    @entity_api.doc(description='Update the metadata of an entity')
    @entity_api.response(201, 'Success')
    def post(self, entity_id):
        args = reqparser.parse_args()
        for [prop, obj] in args.relationships:
            self.db.add_triple(':' + entity_id, prop, ':' + obj)
        return 'Success', 201


@entity_api.route('/', methods=['get', 'post'], strict_slashes=False)
class Entities(Resource):
    @inject
    def __init__(self, db: BrickSparql, api):
        self.db = db
        super(Entities, self).__init__(api)

    @entity_api.marshal_with(entity_model)
    @entity_api.doc(description='List all entities with their types')
    @entity_api.response(200, 'TODO')
    @entity_api.response(401, 'Server Error')
    @entity_api.param('entity_id', 'The ID of an entity for the data request.')
    def get(self):
        # TODO: Implement
        raise exceptions.NotImplemented('TODO: List all entities and types')
        return res

    def add_entities_ttl(self, raw_ttl):
        self.db.update(raw_ttl)

    def add_entities_json(self, entities):
        for entity in entities:
            entity_type = entity['type']
            entity_id = entity.get('entity_id', None)
            if not entity_id:
                entity_id = str(gen_uuid())
                entity['entity_id'] = entity_id
            self.db.add_brick_instance(entity_id, entity_type)
            for prop, obj in entity['relationships']:
                self.db.add_triple(':' + entity_id, prop, ':' + obj)
            name = entity.get('name', None)
            if name:
                self.db.add_triple(':' + entity_id, 'bf:hasName', name)
        return entities

    @entity_api.doc(description='Add entities with their triples.')
    @entity_api.response(201, 'Success', model=entities_model)
    @entity_api.marshal_with(entities_model)
    def post(self):
        args = reqparser.parse_args()
        content_type = args.content_type
        # TODO: Verify/Authorize the user for the turtle file
        if content_type == 'application/json':
            entities = marshal(args, entities_model)['entities']
            entities = self.add_entities_json(entities)
        elif content_type == 'text/turtle':
            raise exceptions.NotImplemented('TODO: Implement entities addition for Content-Type {0}.'.format(content_type))
            raw_ttl = request.data.decode('utf-8')
            self.add_entities_ttl(raw_ttl)
        else:
            raise exceptions.NotImplemented('TODO: Implement entities addition for Content-Type {0}.'.format(content_type))
        return {'entities': entities}, 201