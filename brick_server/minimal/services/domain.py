import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, File, Path, UploadFile
from fastapi_restful.cbv import cbv
from loguru import logger

from brick_server.minimal import models, schemas
from brick_server.minimal.config.manager import settings
from brick_server.minimal.interfaces import AsyncpgTimeseries, GraphDB
from brick_server.minimal.securities.checker import PermissionChecker
from brick_server.minimal.utilities.dependencies import (
    get_graphdb,
    get_path_domain,
    get_ts_db,
)
from brick_server.minimal.utilities.exceptions import BizError, ErrorCode

# from brick_server.minimal.auth.checker import PermissionChecker, PermissionType


router = APIRouter(prefix="/domains", tags=["domains"])


@cbv(router)
class DomainRoute:
    graphdb: GraphDB = Depends(get_graphdb)
    ts_db: AsyncpgTimeseries = Depends(get_ts_db)

    async def initialize_rdf_schema(self, graphs, domain, url):
        if url in graphs:
            logger.info("GraphDB schema {} found in domain {}.", url, domain.name)
        else:
            logger.info(
                "GraphDB schema {} not found in domain {}, initializing...",
                url,
                domain.name,
            )
            await self.graphdb.import_schema_from_url(domain.name, url)

    async def initialize_domain_background(self, domain: models.Domain):
        tasks = [
            self.graphdb.init_repository(domain.name),
            self.ts_db.init_table(domain.name),
            self.ts_db.init_history_table(domain.name),
        ]
        await asyncio.gather(*tasks)
        graphs = await self.graphdb.list_graphs(domain.name)
        await self.initialize_rdf_schema(graphs, domain, settings.DEFAULT_BRICK_URL)
        await self.initialize_rdf_schema(
            graphs, domain, settings.DEFAULT_REF_SCHEMA_URL
        )
        domain.initialized = True
        await domain.save()

    @router.get(
        "/",
        dependencies=[Depends(PermissionChecker())],
    )
    async def list_domains(
        self,
    ) -> schemas.StandardListResponse[schemas.DomainRead]:
        domains = await models.Domain.find_all().to_list()
        return schemas.StandardListResponse(
            [schemas.DomainRead.model_validate(domain.dict()) for domain in domains]
        )

    @router.post(
        "/{domain}",
        dependencies=[
            Depends(PermissionChecker(permission_scope=schemas.PermissionScope.SITE)),
        ],
    )
    async def create_domain(
        self,
        background_tasks: BackgroundTasks,
        domain: str = Path(...),
    ) -> schemas.StandardResponse[schemas.DomainRead]:
        created_domain = models.Domain(name=domain)
        try:
            await created_domain.save()
        except Exception:
            raise BizError(ErrorCode.DomainAlreadyExistsError)
        background_tasks.add_task(self.initialize_domain_background, created_domain)
        return schemas.DomainRead.model_validate(created_domain.dict()).to_response()

    @router.delete(
        "/{domain}",
        dependencies=[
            Depends(PermissionChecker(permission_scope=schemas.PermissionScope.SITE)),
        ],
    )
    async def delete_domain(
        self,
        domain: models.Domain = Depends(get_path_domain),
    ) -> schemas.StandardResponse[schemas.Empty]:
        # TODO: delete repository, add lock
        await domain.delete()
        return schemas.StandardResponse()

    @router.get(
        "/{domain}",
        dependencies=[Depends(PermissionChecker())],
    )
    async def get_domain(
        self,
        domain: models.Domain = Depends(get_path_domain),
    ) -> schemas.StandardResponse[schemas.DomainRead]:
        return schemas.DomainRead.model_validate(domain.dict()).to_response()

    @router.get(
        "/{domain}/init",
        dependencies=[
            Depends(PermissionChecker(permission_scope=schemas.PermissionScope.DOMAIN))
        ],
    )
    async def init_domain(
        self,
        domain: models.Domain = Depends(get_path_domain),
    ) -> schemas.StandardResponse[schemas.DomainRead]:
        # for debug purpose
        await self.initialize_domain_background(domain)
        return schemas.DomainRead.model_validate(domain.dict()).to_response()

    @router.post(
        "/{domain}/upload",
        description="Upload a Turtle file. An example file: https://gitlab.com/jbkoh/brick-server-dev/blob/dev/examples/data/bldg.ttl",
        summary="Uplaod a Turtle file",
        dependencies=[
            Depends(PermissionChecker(permission_scope=schemas.PermissionScope.DOMAIN)),
        ],
    )
    async def upload_turtle_file(
        self,
        background_tasks: BackgroundTasks,
        domain: models.Domain = Depends(get_path_domain),
        file: UploadFile = File(...),
    ) -> schemas.StandardResponse[schemas.DomainRead]:
        await self.graphdb.clear_import_file(domain.name, file.filename)
        await self.graphdb.import_schema_from_file(
            domain.name, file, named_graph=None, delete=False
        )
        # background_tasks.add_task(
        #     self.graphdb.import_schema_from_file,
        #     domain.name,
        #     file,
        #     named_graph=None,
        #     delete=False,
        # )
        return schemas.DomainRead.model_validate(domain.dict()).to_response()
