from pdb import set_trace as bp
from copy import deepcopy
from uuid import uuid4 as gen_uuid
from io import StringIO
import asyncio
from typing import ByteString, Any, Dict, Callable
from collections import defaultdict

import arrow
import rdflib
from rdflib import RDF, URIRef
from fastapi_utils.cbv import cbv
from fastapi import Depends, Header, HTTPException, Body, Query, Path
from fastapi_utils.inferring_router import InferringRouter
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request

from .models import Entity, Relationships, EntityIds, Entities, IsSuccess
from .models import EntitiesCreateResponse, CreateEntitiesRequest
from .models import entity_id_desc, graph_desc, jwt_security_scheme, relationships_desc, entity_desc
from .namespaces import URN, UUID
from ..dbs import BrickSparqlAsync
from ..helpers import striding_windows

from ..auth.authorization import auth_scheme, parse_jwt_token, authorized, authorized_arg, R, O
from ..models import get_all_relationships
from ..configs import configs
from ..dependencies import get_brick_db, dependency_supplier

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
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)

    @entity_router.post('/upload',
                        status_code=200,
                        response_model=IsSuccess,
                        description='Upload a Turtle file. An example file: https://gitlab.com/jbkoh/brick-server-dev/blob/dev/examples/data/bldg.ttl',
                        summary='Uplaod a Turtle file',
                        tags=['Entities'],
                        )
    @authorized
    async def upload(self,
                     request: Request,
                     turtle: str = Body(...,
                                        media_type='text/turtle',
                                        description='The text of a Turtle file.'),
                     add_owner: bool = Query(True,
                                             description='If true, add the current user as an owner of all the entities in the graph.',
                                             ),
                     graph: str = Query(configs['brick']['base_graph'],
                                        description=graph_desc,
                                        ),
                     content_type: str = Header('text/turtle'),
                     token: HTTPAuthorizationCredentials = jwt_security_scheme,
                     ) -> IsSuccess:
        jwt_payload = parse_jwt_token(token.credentials)
        user_id = jwt_payload['user_id']

        if content_type == 'text/turtle':
            ttl_io = StringIO(turtle)
            ttl_backup = deepcopy(ttl_io)
            await self.brick_db.load_rdffile(ttl_io, graph=graph)
            if add_owner:
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
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)


    @entity_router.get('/{entity_id}',
                       status_code=200,
                       response_model=Entity,
                       description='Get information about an entity including type and its relationships with others. The definition of entity: {0}'.format(entity_desc),
                       tags=['Entities'],
                       )
    @authorized_arg(R)
    async def get_entity_by_id(self,
                               request: Request,
                               entity_id: str = Path(..., description=entity_id_desc),
                               token: HTTPAuthorizationCredentials = jwt_security_scheme,
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
                          tags=['Entities'],
                          )
    @authorized_arg(O)
    async def entity_delete(self,
                            request: Request,
                            entity_id: str = Path(..., description=entity_id_desc),
                            token: HTTPAuthorizationCredentials = jwt_security_scheme,
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
                        tags=['Entities'],
                        )
    @authorized_arg(O)
    async def update_entity(self,
                            request: Request,
                            entity_id: str = Path(..., description=entity_id_desc),
                            relationships: Relationships = Body(..., description=relationships_desc),
                            token: HTTPAuthorizationCredentials = jwt_security_scheme,
                            ):
        for [prop, obj] in relationships:
            self.brick_db.add_triple(URIRef(entity_id), prop, obj)
        return 'Success', 200



#TODO: In the auth model, this resource's target is a `graph`
@cbv(entity_router)
class EntitiesResource:

    brick_db: BrickSparqlAsync = Depends(get_brick_db)
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)


    @entity_router.get('/',
                       status_code=200,
                       response_model=EntityIds,
                       description='List all entities with their types.',
                       tags=['Entities'],
                       )
    @authorized #TODO: Think about the auth logic for access those.
    async def get(self,
                  request: Request,
                  token: HTTPAuthorizationCredentials = jwt_security_scheme,
                  ) -> EntityIds:
        qstr = """
        select ?entity where {
        ?entity a/rdfs:subClassOf* bf:TagSet.
        }
        """ # TODO The query should be generalized to Class
        res = await self.brick_db.query(qstr)
        entity_ids = [row['entity']['value'] for row in res['results']['bindings']]
        return EntityIds(entity_ids=entity_ids)

    @entity_router.post('/',
                        status_code=200,
                        response_model=EntitiesCreateResponse,
                        description='Add entities with their triples.',
                        tags=['Entities'],
                        )
    @authorized
    async def post(self,
                   request: Request,
                   create_entities: CreateEntitiesRequest = Body(..., description='A dictionary to describe entities to create. Keys are Brick Classes and values are the number of instances to create for the Class'),
                   graph: str = Query(configs['brick']['base_graph'], description=graph_desc),
                   token: HTTPAuthorizationCredentials = jwt_security_scheme,
                   ) -> EntitiesCreateResponse:
        resp = defaultdict(list)
        for brick_type, entities_num in create_entities.items():
            for _ in range(entities_num):
                uri = UUID[str(gen_uuid())]
                await self.brick_db.add_triple(uri, RDF.type, URIRef(brick_type))
                # TODO: Check the brick_type based on the parameter in the future
                resp[brick_type].append(str(uri))
        return dict(resp)

    async def add_entities_json_deprecated(self, entities):
        #TODO: IMplement this:
        raise HTTPException(status_code=501)
        for entity in entities:
            entity_type = entity['type']
            entity_id = entity.get('entity_id', None)
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
