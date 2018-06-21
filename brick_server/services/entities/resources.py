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

from .models import reqparser, entity_api
from .models import entity_model, entities_model, relationships_model
from brick_server.extensions.lockmanager import LockManager


def get_entity_type(db, entity_id):
    qstr = """
    select ?o where {{
    :{0} a ?o.
    }}
    """.format(entity_id)
    res = db.query(qstr)
    tuples = res['tuples']
    if tuples:
        assert len(tuples) == 1
        return tuples[0][0]
    else:
        #Type not found for the entity_id
        return None

def get_name(db, entity_id):
    qstr = """
    select ?name where {{
        :{0} bf:hasName ?name.
    }}
    """.format(entity_id)
    res = db.query(qstr)
    tuples = res['tuples']
    if tuples:
        name = tuples[0][0]
    else:
        name = None
    return name

def get_all_relationships(db, entity_id):
    #TODO: Implement owl:inverseOf inside Vrituoso
    print('warning: ``inverseOf`` is not implemented yet inside Virtuoso')
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
    return res['tuples']


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
        if not entity_type:
            raise exceptions.NotFound('{0} does not exist'.format(entity_id))
        relationships = get_all_relationships(self.db, entity_id)
        name = get_name(self.db, entity_id)
        res = {
            'type': entity_type,
            'relationships': relationships,
            'name': name,
            'entity_id': entity_id,
        }
        return res

    @entity_api.doc(description='Delete an entity along with its relationships and data')
    @entity_api.param('entity_id', 'The ID of an entity for the data request.')
    @entity_api.response(200, 'Sucess')
    def delete(self, entity_id):
        raise exceptions.NotImplemented('TODO: Delete corresponding entity.')
        return None

    @entity_api.doc(description='Add relationships of an entity')
    @entity_api.expect(relationships_model, validate=True) # TODO: Enable this line.
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

    @entity_api.doc(description='List all entities with their types. (Not implemented yet)')
    @entity_api.response(200, 'TODO')
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
    @entity_api.expect(entities_model, validate=True) # TODO: Enable this line.
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
