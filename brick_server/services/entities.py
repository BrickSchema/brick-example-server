import pdb
from copy import deepcopy
from uuid import uuid4 as gen_uuid
from io import StringIO
import asyncio
from typing import ByteString, Any, Dict

import arrow
import rdflib
from rdflib import URIRef
from fastapi_utils.cbv import cbv
from fastapi import Depends, Header, HTTPException, Body, Query, Security
from fastapi_utils.inferring_router import InferringRouter
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request

from .models import Entity, Relationships, EntityIds, Entities, IsSuccess
from ..dbs import BrickSparqlAsync
from ..helpers import striding_windows

from ..auth.authorization import authorized_isadmin, auth_scheme, parse_jwt_token
from ..models import get_all_relationships
from ..configs import configs
from ..dbs import get_brick_db

entity_router = InferringRouter('entities')



async def get_entity_type(db, entity_id):
    qstr = """
    select ?o where {{
    <{0}> a ?o.
    }}
    """.format(entity_id)
    res = await db.query(qstr)
    entity_types = [row['o']['value'] for row in res['results']['bindings']]
    if entity_types:
        #assert len(entity_types) == 1 # TODO: This should be changed
        return entity_types[0]
    else:
        # Type not found for the entity_id
        return None


async def get_name(db, entity_id):
    qstr = """
    select ?name where {{
        <{0}> bf:hasName ?name.
    }}
    """.format(entity_id)
    res = await db.query(qstr)
    bindings = res['results']['bindings']
    if bindings:
        name = bindings[0]['name']['value']
    else:
        name = None
    return name


@cbv(entity_router)
class EntitiesByFileResource:

    brick_db: BrickSparqlAsync = Depends(get_brick_db)

    @entity_router.post('/upload',
                        status_code=200,
                        response_model=IsSuccess,
                        description='Upload a Turtle file. An example file: https://gitlab.com/jbkoh/brick-server-dev/blob/dev/examples/data/bldg.ttl',
                        summary='Uplaod a Turtle file',
                        )
    @authorized_isadmin
    async def upload(self,
                     request: str = Body(..., media_type='text/turtle'),
                     graph: str = Query(configs['brick']['base_graph']),
                     content_type: str = Header('text/turtle'),
                     token: HTTPAuthorizationCredentials = Security(auth_scheme),
                     ) -> IsSuccess:
        jwt_payload = parse_jwt_token(token.credentials)
        user_id = jwt_payload['user_id']

        if content_type == 'text/turtle':
            #pdb.set_trace()
            #req_bytes = await request.body()
            #ttl_io = StringIO(req_bytes.decode('utf-8'))
            ttl_io = StringIO(request)
            #ttl_io = StringIO(request.data.decode('utf-8'))
            ttl_backup = deepcopy(ttl_io)
            await self.brick_db.load_rdffile(ttl_io, graph=graph)
            #self.brick_db.load_rdffile(ttl_io, graph=graph)
            g = rdflib.Graph()
            g.parse(ttl_backup, format='turtle')
            res = g.query("""
            select ?s where {
                ?s a ?o.
            }
            """)
            user_entity = URIRef(user_id)
            res = list(res)
            for rows in striding_windows(res, 500):
                new_triples = []
                for row in rows:
                    entity = row[0]
                    new_triples.append((URIRef(entity), self.brick_db.BRICK.hasOwner, user_entity))
                await self.brick_db.add_triples(new_triples)
        else:
            raise HTTPException(status_code=405, detail='{0} is not supported'.format(content_type))
        return IsSuccess()

@cbv(entity_router)
class EntitiesByIdResource:

    brick_db: BrickSparqlAsync = Depends(get_brick_db)


    @entity_router.get('/{entity_id}',
                       status_code=200,
                       response_model=Entity,
                       description='Get information about an entity including type and its relationships with others',
                       )
    @authorized_isadmin
    async def get_entity_by_id(self,
                               entity_id,
                               token: HTTPAuthorizationCredentials = Security(auth_scheme),
                               ) -> Entity:
        entity_type = await get_entity_type(self.brick_db, entity_id)
        if not entity_type:
            raise HTTPException(status_code=404, detail='{0} does not exist'.format(entity_id))
        relationships = await get_all_relationships(self.brick_db, entity_id)
        name = await get_name(self.brick_db, entity_id)
        entity = Entity(
            type=entity_type,
            relationships=relationships,
            name=name,
            entity_id=entity_id,
        )
        return entity

    @entity_router.delete('/{entity_id}',
                          status_code=200,
                          response_model=IsSuccess,
                          description='Delete an entity along with its relationships and data',
                          )
    @authorized_isadmin
    async def entity_delete(self,
                            entity_id,
                            token: HTTPAuthorizationCredentials = Security(auth_scheme),
                            ) -> IsSuccess:
        futures = []
        qstr = """
        delete {{
            <{entity_id}> ?p ?o.
        }}
        WHERE {{
            <{entity_id}> ?p ?o.
        }}
        """.format(entity_id=entity_id)
        futures.append(self.brick_db.query(qstr, is_update=True, is_delete=True))

        qstr = """
        delete {{
            ?s ?p <{entity_id}>.
        }}
        WHERE {{
            ?s ?p <{entity_id}>.
        }}
        """.format(entity_id=entity_id)
        futures.append(self.brick_db.query(qstr, is_update=True, is_delete=True))

        await asyncio.gather(*futures)
        return IsSuccess()

    @entity_router.post('/{entity_id}',
                        status_code=200,
                        response_model=IsSuccess,
                        description='Add relationships of an entity',
                        )
    @authorized_isadmin
    async def update_entity(self,
                            entity_id,
                            relationships: Relationships,
                            token: HTTPAuthorizationCredentials = Security(auth_scheme),
                            ):
        for [prop, obj] in relationships:
            self.db.add_triple(URIRef(entity_id), prop, obj)
        return 'Success', 200

#@cbv(entity_router)
#class Testtt:
#
#    brick_db: BrickSparqlAsync = Depends(get_brick_db)
#
#
#    @entity_router.get('/testtt/testtt',
#                       status_code=200,
#                       response_model=IsSuccess,
#                       )
#    async def get(self) -> IsSuccess:
#        return IsSuccess()
#
@cbv(entity_router)
class EntitiesResource:

    brick_db: BrickSparqlAsync = Depends(get_brick_db)


    @entity_router.get('/',
                       status_code=200,
                       response_model=EntityIds,
                       description='List all entities with their types.',
                       )
    @authorized_isadmin
    async def get(self,
                  token: HTTPAuthorizationCredentials = Security(auth_scheme),
                  ) -> EntityIds:
        # TODO: Implement
        qstr = """
        select ?entity where {
        ?entity a/rdfs:subClassOf* brick:TagSet.
        }
        """ # TODO The query should be generalized to Class
        res = await self.db.query(qstr)
        pdb.set_trace()
        resp = {
            'entity_ids': [row[0] for row in res['tuples']],
        }
        #raise exceptions.NotImplemented('TODO: List all entities and types')
        return resp

    @entity_router.post('/',
                        status_code=200,
                        response_model=IsSuccess,
                        description='Add entities with their triples.',
                        )
    @authorized_isadmin
    async def post(self,
                   entities: Entities,
                   graph: str = configs['brick']['base_graph'],
                   token: HTTPAuthorizationCredentials = Security(auth_scheme),
                   ) -> IsSuccess:
        entities = marshal(args, entities_model)['entities']
        await self.add_entities_json(entities.dict())
        return IsSuccess()

    async def add_entities_json(self, entities):
        #TODO: IMplement this:
        raise HTTPException(status_code=501)
        for entity in entities:
            entity_type = entity['type']
            entity_id = entity.get('entity_id', 'Success')
            if not entity_id:
                entity_id = str(gen_uuid())
                entity['entity_id'] = entity_id
            entity_id = URIRef(entity_id)
            self.brick_db.add_brick_instance(entity_id, entity_type)
            for prop, obj in entity['relationships']:
                obj = URIRef(obj)
                self.brick_db.add_triple(entity_id, prop, obj)
            name = entity.get('name', None)
            if name:
                self.brick_db.add_triple(entity_id, 'bf:hasName', name)
        return entities
