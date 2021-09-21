import asyncio
from collections import defaultdict
from copy import deepcopy
from io import StringIO
from typing import Callable, List
from uuid import uuid4 as gen_uuid

import rdflib
from fastapi import Body, Depends, Header, HTTPException, Path, Query
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_rest_framework.config import settings
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from rdflib import RDF, URIRef
from starlette.requests import Request

from brick_server.minimal.auth.authorization import (
    O,
    R,
    authorized,
    authorized_arg,
    parse_jwt_token,
)
from brick_server.minimal.dbs import BrickSparqlAsync
from brick_server.minimal.dependencies import dependency_supplier, get_brick_db
from brick_server.minimal.descriptions import Descriptions
from brick_server.minimal.helpers import striding_windows
from brick_server.minimal.interfaces.namespaces import UUID
from brick_server.minimal.models import get_all_relationships
from brick_server.minimal.schemas import (
    CreateEntitiesRequest,
    EntitiesCreateResponse,
    Entity,
    EntityIds,
    IsSuccess,
    Relationships,
    jwt_security_scheme,
)

entity_router = InferringRouter(prefix="/entities", tags=["Entities"])


async def get_entity_type(db, entity_id):
    qstr = """
    select ?o where {{
    <{0}> a ?o.
    }}
    """.format(
        entity_id
    )
    res = await db.query(qstr)
    entity_types = [row["o"]["value"] for row in res["results"]["bindings"]]
    if entity_types:
        # assert len(entity_types) == 1 # TODO: This should be changed
        return entity_types[0]
    else:
        # Type not found for the entity_id
        return None


async def get_name(db, entity_id):
    qstr = """
    select ?name where {{
        <{0}> bf:hasName ?name.
    }}
    """.format(
        entity_id
    )
    res = await db.query(qstr)
    bindings = res["results"]["bindings"]
    if bindings:
        name = bindings[0]["name"]["value"]
    else:
        name = None
    return name


@cbv(entity_router)
class EntitiesByFileResource:

    brick_db: BrickSparqlAsync = Depends(get_brick_db)
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)

    @entity_router.post(
        "/upload",
        status_code=200,
        response_model=IsSuccess,
        description="Upload a Turtle file. An example file: https://gitlab.com/jbkoh/brick-server-dev/blob/dev/examples/data/bldg.ttl",
        summary="Uplaod a Turtle file",
    )
    @authorized
    async def upload(
        self,
        request: Request,
        turtle: str = Body(
            ..., media_type="text/turtle", description="The text of a Turtle file."
        ),
        add_owner: bool = Query(
            True,
            description="If true, add the current user as an owner of all the entities in the graph.",
        ),
        graph: str = Query(
            settings.brick_base_graph,
            description=Descriptions.graph,
        ),
        content_type: str = Header("text/turtle"),
        token: HTTPAuthorizationCredentials = jwt_security_scheme,
    ) -> IsSuccess:
        jwt_payload = parse_jwt_token(token.credentials)
        user_id = jwt_payload["user_id"]

        if content_type == "text/turtle":
            ttl_io = StringIO(turtle)
            ttl_backup = deepcopy(ttl_io)
            await self.brick_db.load_rdffile(ttl_io, graph=graph)
            if add_owner:
                g = rdflib.Graph()
                g.parse(ttl_backup, format="turtle")
                res = g.query(
                    """
                select ?s where {
                    ?s a ?o.
                }
                """
                )
                user_entity = URIRef(user_id)
                res = list(res)
                for rows in striding_windows(res, 500):
                    new_triples = []
                    for row in rows:
                        entity = row[0]
                        new_triples.append(
                            (URIRef(entity), self.brick_db.BRICK.hasOwner, user_entity)
                        )
                    await self.brick_db.add_triples(new_triples)
        else:
            raise HTTPException(
                status_code=405, detail="{} is not supported".format(content_type)
            )
        return IsSuccess()


@cbv(entity_router)
class EntitiesByIdResource:

    brick_db: BrickSparqlAsync = Depends(get_brick_db)
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)

    @entity_router.get(
        "/{entity_id:path}",
        status_code=200,
        response_model=Entity,
        description="Get information about an entity including type and its relationships with others. The definition of entity: {}".format(
            Descriptions.entity
        ),
    )
    @authorized_arg(R)
    async def get_entity_by_id(
        self,
        request: Request,
        entity_id: str = Path(..., description=Descriptions.entity_id),
        token: HTTPAuthorizationCredentials = jwt_security_scheme,
    ) -> Entity:
        entity_type = await get_entity_type(self.brick_db, entity_id)
        if not entity_type:
            raise HTTPException(
                status_code=404, detail="{} does not exist".format(entity_id)
            )
        relationships = await get_all_relationships(self.brick_db, entity_id)
        name = await get_name(self.brick_db, entity_id)
        entity = Entity(
            type=entity_type,
            relationships=relationships,
            name=name,
            entity_id=entity_id,
        )
        return entity

    @entity_router.delete(
        "/{entity_id}",
        status_code=200,
        response_model=IsSuccess,
        description="Delete an entity along with its relationships and data",
    )
    @authorized_arg(O)
    async def entity_delete(
        self,
        request: Request,
        entity_id: str = Path(..., description=Descriptions.entity_id),
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
        """.format(
            entity_id=entity_id
        )
        futures.append(self.brick_db.query(qstr, is_update=True, is_delete=True))

        qstr = """
        delete {{
            ?s ?p <{entity_id}>.
        }}
        WHERE {{
            ?s ?p <{entity_id}>.
        }}
        """.format(
            entity_id=entity_id
        )
        futures.append(self.brick_db.query(qstr, is_update=True, is_delete=True))

        await asyncio.gather(*futures)
        return IsSuccess()

    @entity_router.post(
        "/{entity_id}",
        status_code=200,
        response_model=IsSuccess,
        description="Add relationships of an entity",
    )
    @authorized_arg(O)
    async def update_entity(
        self,
        request: Request,
        entity_id: str = Path(..., description=Descriptions.entity_id),
        relationships: Relationships = Body(
            ..., description=Descriptions.relationships
        ),
        token: HTTPAuthorizationCredentials = jwt_security_scheme,
    ):
        for [prop, obj] in relationships:
            self.brick_db.add_triple(URIRef(entity_id), prop, obj)
        return "Success", 200


def get_brick_relation_base(brick_version):  # TODO: Implement this in brick-data.
    version_parts = brick_version.split(".")
    major = int(version_parts[0])
    minor = int(version_parts[1])
    if major >= 1 and minor >= 1:
        return "brick"
    else:
        return "bf"


def get_brick_topclass(brick_version):  # TODO: Implement this in brick-data.
    version_parts = brick_version.split(".")
    major = int(version_parts[0])
    minor = int(version_parts[1])
    if major >= 1 and minor >= 1:
        return "brick:Class"
    else:
        return "bf:TagSet"


brick_predicates = [
    "hasPoint",
    "isPointOf",
    "hasPart",
    "isPartOf",
    "hasLocation",
    "isLocationOf",
    "feeds",
    "isFedBy",
]


# TODO: In the auth model, this resource's target is a `graph`
@cbv(entity_router)
class EntitiesResource:

    brick_db: BrickSparqlAsync = Depends(get_brick_db)
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)

    @entity_router.get(
        "/",
        status_code=200,
        response_model=EntityIds,
        description="List all entities with their types and relations.",
    )
    @authorized  # TODO: Think about the auth logic for access those.
    async def get(
        self,
        request: Request,
        hasPoint: List[str] = Query([], description=Descriptions.relation_query),
        isPointOf: List[str] = Query([], description=Descriptions.relation_query),
        hasPart: List[str] = Query([], description=Descriptions.relation_query),
        isPartOf: List[str] = Query([], description=Descriptions.relation_query),
        hasLocation: List[str] = Query([], description=Descriptions.relation_query),
        isLocationOf: List[str] = Query([], description=Descriptions.relation_query),
        feeds: List[str] = Query([], description=Descriptions.relation_query),
        isFedBy: List[str] = Query([], description=Descriptions.relation_query),
        token: HTTPAuthorizationCredentials = jwt_security_scheme,
    ) -> EntityIds:
        topclass = get_brick_topclass(self.brick_db.BRICK_VERSION)
        qstr = f"""
        select ?entity where {{
        ?entity a/rdfs:subClassOf* {topclass}.
        """  # TODO The query should be generalized to Class
        for predicate in brick_predicates:
            objects = locals()[predicate]
            for object in objects:
                qstr += f"?entity brick:{predicate} <{object}>.\n"  # TODO: Parameterize property base between bf vs brick.
        qstr += "}"
        print(qstr)
        res = await self.brick_db.query(qstr)
        entity_ids = [row["entity"]["value"] for row in res["results"]["bindings"]]
        return EntityIds(entity_ids=entity_ids)

    @entity_router.post(
        "/",
        status_code=200,
        response_model=EntitiesCreateResponse,
        description="Add entities with their triples.",
    )
    @authorized
    async def post(
        self,
        request: Request,
        create_entities: CreateEntitiesRequest = Body(
            ...,
            description="A dictionary to describe entities to create. Keys are Brick Classes and values are the number of instances to create for the Class",
        ),
        graph: str = Query(settings.brick_base_graph, description=Descriptions.graph),
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
        # TODO: IMplement this:
        raise HTTPException(status_code=501)
        for entity in entities:
            entity_type = entity["type"]
            entity_id = entity.get("entity_id", None)
            if not entity_id:
                entity_id = str(gen_uuid())
                entity["entity_id"] = entity_id
            entity_id = URIRef(entity_id)
            self.brick_db.add_brick_instance(entity_id, entity_type)
            for prop, obj in entity["relationships"]:
                obj = URIRef(obj)
                self.brick_db.add_triple(entity_id, prop, obj)
            name = entity.get("name", None)
            if name:
                self.brick_db.add_triple(entity_id, "bf:hasName", name)
        return entities
