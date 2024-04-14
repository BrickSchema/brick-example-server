from typing import Any, Callable, List

from fastapi import Body, Depends, HTTPException, Query
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter
from loguru import logger
from pydantic import BaseModel
from starlette.requests import Request

from brick_server.minimal.config.manager import settings
from brick_server.minimal.interfaces import GraphDB
from brick_server.minimal.models import Domain
from brick_server.minimal.schemas import Entity, EntityIds
from brick_server.minimal.securities.checker import (
    PermissionChecker,
    PermissionCheckerWithEntityId,
    PermissionType,
)
from brick_server.minimal.utilities.dependencies import (
    dependency_supplier,
    get_graphdb,
    query_domain,
)
from brick_server.minimal.utilities.descriptions import Descriptions

entity_router = InferringRouter(tags=["Entities"])


async def get_entity_types(db: GraphDB, domain: Domain, entity_id) -> List[str]:
    qstr = """
    select ?o where {{
    <{0}> a ?o.
    }}
    """.format(
        entity_id
    )
    res = await db.query(domain.name, qstr)
    entity_types = [row["o"]["value"] for row in res["results"]["bindings"]]
    logger.debug(entity_types)
    return entity_types
    # if entity_types:
    #     # assert len(entity_types) == 1 # TODO: This should be changed
    #     return entity_types[0]
    # else:
    #     # Type not found for the entity_id
    #     return None


async def get_all_relationships(db: GraphDB, domain: Domain, entity_id: str):
    # TODO: Implement owl:inverseOf inside Vrituoso
    print("warning: ``inverseOf`` is not implemented yet inside Virtuoso")
    qstr = """
    select ?p ?o where {{
    {{
    <{0}> ?p ?o.
    FILTER NOT EXISTS {{ <{0}> a ?o .}}
    }}
    UNION
    {{
    ?inverse_p owl:inverseOf ?p .
    ?o ?inverse_p <{0}>.
    }}
    }}
    """.format(
        entity_id
    )
    res = await db.query(domain.name, qstr)
    return [
        (row["p"]["value"], row["o"]["value"]) for row in res["results"]["bindings"]
    ]


async def get_name(graphdb, domain: Domain, entity_id: str):
    qstr = """
    select ?name where {{
        <{0}> brick:hasName ?name.
    }}
    """.format(
        entity_id
    )
    res = await graphdb.query(domain.name, qstr)
    bindings = res["results"]["bindings"]
    if bindings:
        name = bindings[0]["name"]["value"]
    else:
        name = None
    return name


# moved to domain.py
# @cbv(entity_router)
# class EntitiesByFileResource:
#     auth_logic: Callable = Depends(dependency_supplier.auth_logic)
#     graphdb: GraphDB = Depends(get_graphdb)
#
#     @entity_router.post(
#         "/upload",
#         status_code=200,
#         response_model=IsSuccess,
#         description="Upload a Turtle file. An example file: https://gitlab.com/jbkoh/brick-server-dev/blob/dev/examples/data/bldg.ttl",
#         summary="Uplaod a Turtle file",
#     )
#     async def upload(
#         self,
#         background_tasks: BackgroundTasks,
#         file: UploadFile = File(...),
#         named_graph: Optional[str] = Query(None, description=Descriptions.graph),
#         checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
#     ):
#         await self.graphdb.clear_import_file(file.filename)
#         background_tasks.add_task(
#             self.graphdb.import_schema_from_file, file, named_graph, delete=False
#         )
#         # await self.graphdb.import_schema_from_file(file, named_graph, delete=True)
#         return IsSuccess()

# @entity_router.post(
#     "/upload",
#     status_code=200,
#     response_model=IsSuccess,
#     description="Upload a Turtle file. An example file: https://gitlab.com/jbkoh/brick-server-dev/blob/dev/examples/data/bldg.ttl",
#     summary="Uplaod a Turtle file",
# )
# async def upload(
#     self,
#     request: Request,
#     turtle: str = Body(
#         ..., media_type="text/turtle", description="The text of a Turtle file."
#     ),
#     add_owner: bool = Query(
#         True,
#         description="If true, add the current user as an owner of all the entities in the graph.",
#     ),
#     graph: str = Query(
#         settings.brick_base_graph,
#         description=Descriptions.graph,
#     ),
#     content_type: str = Header("text/turtle"),
#     token: HTTPAuthorizationCredentials = jwt_security_scheme,
#     checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
# ) -> IsSuccess:
#     jwt_payload = parse_jwt_token(token.credentials)
#     user_id = jwt_payload["user_id"]
#
#     if content_type == "text/turtle":
#         ttl_io = StringIO(turtle)
#         ttl_backup = deepcopy(ttl_io)
#         await self.brick_db.load_rdffile(ttl_io, graph=graph)
#         if add_owner:
#             g = rdflib.Graph()
#             g.parse(ttl_backup, format="turtle")
#             res = g.query(
#                 """
#             select ?s where {
#                 ?s a ?o.
#             }
#             """
#             )
#             user_entity = URIRef(user_id)
#             res = list(res)
#             for rows in striding_windows(res, 500):
#                 new_triples = []
#                 for row in rows:
#                     entity = row[0]
#                     new_triples.append(
#                         (URIRef(entity), self.brick_db.BRICK.hasOwner, user_entity)
#                     )
#                 await self.brick_db.add_triples(new_triples)
#     else:
#         raise HTTPException(
#             status_code=405, detail="{} is not supported".format(content_type)
#         )
#     return IsSuccess()


@cbv(entity_router)
class EntitiesByIdResource:
    auth_logic: Callable = Depends(dependency_supplier.auth_logic)
    graphdb: GraphDB = Depends(get_graphdb)

    @entity_router.get(
        "/",
        status_code=200,
        response_model=Entity,
        description="Get information about an entity including type and its relationships with others. The definition of entity: {}".format(
            Descriptions.entity
        ),
    )
    async def get_entity_by_id(
        self,
        request: Request,
        entity_id: str = Query(..., description=Descriptions.entity_id),
        domain: Domain = Depends(query_domain),
        checker: Any = Depends(PermissionCheckerWithEntityId(PermissionType.READ)),
    ) -> Entity:
        print(entity_id)
        entity_types = await get_entity_types(self.graphdb, domain, entity_id)
        if not entity_types:
            raise HTTPException(
                status_code=404, detail="{} does not exist".format(entity_id)
            )
        relationships = await get_all_relationships(self.graphdb, domain, entity_id)
        name = await get_name(self.graphdb, domain, entity_id)
        # TODO: add domain in output?
        entity = Entity(
            types=entity_types,
            relationships=relationships,
            name=name,
            entity_id=entity_id,
        )
        return entity

    # @entity_router.delete(
    #     "/{entity_id}",
    #     status_code=200,
    #     response_model=IsSuccess,
    #     description="Delete an entity along with its relationships and data",
    # )
    # async def entity_delete(
    #     self,
    #     request: Request,
    #     entity_id: str = Path(..., description=Descriptions.entity_id),
    #     checker: Any = Depends(PermissionCheckerWithEntityId(PermissionType.WRITE)),
    # ) -> IsSuccess:
    #     futures = []
    #     qstr = """
    #     delete {{
    #         <{entity_id}> ?p ?o.
    #     }}
    #     WHERE {{
    #         <{entity_id}> ?p ?o.
    #     }}
    #     """.format(
    #         entity_id=entity_id
    #     )
    #     futures.append(self.brick_db.query(qstr, is_update=True, is_delete=True))
    #
    #     qstr = """
    #     delete {{
    #         ?s ?p <{entity_id}>.
    #     }}
    #     WHERE {{
    #         ?s ?p <{entity_id}>.
    #     }}
    #     """.format(
    #         entity_id=entity_id
    #     )
    #     futures.append(self.brick_db.query(qstr, is_update=True, is_delete=True))
    #
    #     await asyncio.gather(*futures)
    #     return IsSuccess()

    # @entity_router.post(
    #     "/{entity_id}",
    #     status_code=200,
    #     response_model=IsSuccess,
    #     description="Add relationships of an entity",
    # )
    # async def update_entity(
    #     self,
    #     request: Request,
    #     entity_id: str = Path(..., description=Descriptions.entity_id),
    #     relationships: Relationships = Body(
    #         ..., description=Descriptions.relationships
    #     ),
    #     checker: Any = Depends(PermissionCheckerWithEntityId(PermissionType.WRITE)),
    # ):
    #     for [prop, obj] in relationships:
    #         await self.brick_db.add_triple(URIRef(entity_id), prop, obj)
    #     return "Success", 200


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


class ListEntityParams(BaseModel):
    hasPoint: List[str] = []
    isPointOf: List[str] = []
    hasPart: List[str] = []
    isPartOf: List[str] = []
    hasLocation: List[str] = []
    isLocationOf: List[str] = []
    feeds: List[str] = []
    isFedBy: List[str] = []


# TODO: In the auth model, this resource's target is a `graph`
@cbv(entity_router)
class EntitiesResource:
    auth_logic: Callable = Depends(dependency_supplier.auth_logic)
    graphdb: GraphDB = Depends(get_graphdb)

    @entity_router.post(
        "/list",
        status_code=200,
        response_model=EntityIds,
        description="List all entities with their types and relations.",
    )
    async def post(
        self,
        request: Request,
        params: ListEntityParams = Body(
            ListEntityParams(), description=Descriptions.relation_query
        ),
        domain: Domain = Depends(query_domain),
        checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
    ) -> EntityIds:
        # FIXME: rewrite
        topclass = get_brick_topclass(settings.BRICK_VERSION)
        logger.debug("topclass: {}", topclass)
        qstr = f"""
        select distinct ?entity where {{
        ?entity a/rdfs:subClassOf* {topclass}.
        """  # TODO The query should be generalized to Class
        for predicate, objects in params.dict().items():
            for obj in objects:
                qstr += f"?entity brick:{predicate} {obj}.\n"  # TODO: Parameterize property base between bf vs brick.
        qstr += "}"
        res = await self.graphdb.query(domain.name, qstr)
        entity_ids = [row["entity"]["value"] for row in res["results"]["bindings"]]
        return EntityIds(entity_ids=entity_ids)

    # @entity_router.post(
    #     "/",
    #     status_code=200,
    #     response_model=EntitiesCreateResponse,
    #     description="Add entities with their triples.",
    # )
    # # @authorized
    # async def post(
    #     self,
    #     request: Request,
    #     create_entities: CreateEntitiesRequest = Body(
    #         ...,
    #         description="A dictionary to describe entities to create. Keys are Brick Classes and values are the number of instances to create for the Class",
    #     ),
    #     graph: str = Query(settings.brick_base_graph, description=Descriptions.graph),
    #     checker: Any = Depends(PermissionChecker(PermissionType.READ)),
    # ) -> EntitiesCreateResponse:
    #     resp = defaultdict(list)
    #     for brick_type, entities_num in create_entities.items():
    #         for _ in range(entities_num):
    #             uri = UUID[str(gen_uuid())]
    #             await self.brick_db.add_triple(uri, RDF.type, URIRef(brick_type))
    #             # TODO: Check the brick_type based on the parameter in the future
    #             resp[brick_type].append(str(uri))
    #     return dict(resp)

    # async def add_entities_json_deprecated(self, entities):
    #     # TODO: IMplement this:
    #     raise HTTPException(status_code=501)
    #     for entity in entities:
    #         entity_type = entity["type"]
    #         entity_id = entity.get("entity_id", None)
    #         if not entity_id:
    #             entity_id = str(gen_uuid())
    #             entity["entity_id"] = entity_id
    #         entity_id = URIRef(entity_id)
    #         self.brick_db.add_brick_instance(entity_id, entity_type)
    #         for prop, obj in entity["relationships"]:
    #             obj = URIRef(obj)
    #             self.brick_db.add_triple(entity_id, prop, obj)
    #         name = entity.get("name", None)
    #         if name:
    #             self.brick_db.add_triple(entity_id, "bf:hasName", name)
    #     return entities
