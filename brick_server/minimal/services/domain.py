import asyncio
from typing import Any

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
    # auth_logic: Callable = Depends(dependency_supplier.auth_logic)
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

    @router.post("/{domain}")
    async def create_domain(
        self,
        background_tasks: BackgroundTasks,
        domain: str = Path(...),
        # checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
    ) -> schemas.StandardResponse[schemas.DomainRead]:
        created_domain = models.Domain(name=domain)
        try:
            await created_domain.save()
        except Exception:
            raise BizError(ErrorCode.DomainAlreadyExistsError)
        background_tasks.add_task(self.initialize_domain_background, created_domain)
        return schemas.DomainRead.model_validate(created_domain.dict()).to_response()

    @router.delete("/{domain}")
    async def delete_domain(
        self,
        domain: models.Domain = Depends(get_path_domain),
        # checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
    ) -> schemas.StandardResponse[schemas.Empty]:
        # TODO: delete repository, add lock
        await domain.delete()
        return schemas.StandardResponse()

    @router.get("/{domain}")
    async def get_domain(
        self,
        background_tasks: BackgroundTasks,
        domain: models.Domain = Depends(get_path_domain),
        checker: Any = Depends(PermissionChecker(schemas.PermissionType.READ)),
    ) -> schemas.StandardResponse[schemas.DomainRead]:
        return schemas.DomainRead.model_validate(domain.dict()).to_response()

    @router.get("/{domain}/init")
    async def init_domain(
        self,
        domain: models.Domain = Depends(get_path_domain),
        # checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
    ) -> schemas.StandardResponse[schemas.DomainRead]:
        # for debug purpose
        await self.initialize_domain_background(domain)
        return schemas.DomainRead.model_validate(domain.dict()).to_response()

    @router.post(
        "/{domain}/upload",
        status_code=200,
        description="Upload a Turtle file. An example file: https://gitlab.com/jbkoh/brick-server-dev/blob/dev/examples/data/bldg.ttl",
        summary="Uplaod a Turtle file",
    )
    async def upload_turtle_file(
        self,
        background_tasks: BackgroundTasks,
        domain: models.Domain = Depends(get_path_domain),
        file: UploadFile = File(...),
        # checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
    ) -> schemas.StandardResponse[schemas.DomainRead]:
        await self.graphdb.clear_import_file(domain.name, file.filename)
        background_tasks.add_task(
            self.graphdb.import_schema_from_file,
            domain.name,
            file,
            named_graph=None,
            delete=False,
        )
        # await self.graphdb.import_schema_from_file(file, named_graph, delete=True)
        return schemas.DomainRead.model_validate(domain.dict()).to_response()
