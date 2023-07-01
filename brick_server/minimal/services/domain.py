from typing import Any, Callable

from fastapi import BackgroundTasks, Depends, File, Path, UploadFile
from fastapi_rest_framework.config import settings
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from loguru import logger

from brick_server.minimal import models, schemas
from brick_server.minimal.auth.checker import PermissionChecker, PermissionType
from brick_server.minimal.dependencies import (
    dependency_supplier,
    get_graphdb,
    get_ts_db,
    path_domain,
)
from brick_server.minimal.exceptions import AlreadyExistsError
from brick_server.minimal.interfaces import AsyncpgTimeseries, GraphDB
from brick_server.minimal.schemas import IsSuccess

domain_router = InferringRouter(tags=["Domains"])


@cbv(domain_router)
class DomainRoute:
    auth_logic: Callable = Depends(dependency_supplier.auth_logic)
    graphdb: GraphDB = Depends(get_graphdb)
    ts_db: AsyncpgTimeseries = Depends(get_ts_db)

    async def initialize_domain_background(self, domain: models.Domain):
        await self.graphdb.init_repository(domain.name)
        await self.ts_db.init_table(domain.name)
        await self.ts_db.init_history_table(domain.name)
        graphs = await self.graphdb.list_graphs(domain.name)
        if settings.default_brick_url in graphs:
            logger.info("GraphDB Brick Schema found.")
        else:
            logger.info("GraphDB Brick Schema not found.")
            await self.graphdb.import_schema_from_url(
                domain.name, settings.default_brick_url
            )
        domain.initialized = True
        domain.save()

    @domain_router.post("/{domain}")
    async def create_domain(
        self,
        background_tasks: BackgroundTasks,
        domain: str = Path(...),
        checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
    ) -> schemas.Domain:
        created_domain = models.Domain(name=domain)
        try:
            created_domain.save()
        except Exception:
            raise AlreadyExistsError("domain", "name")
        background_tasks.add_task(self.initialize_domain_background, created_domain)
        return schemas.Domain.from_orm(created_domain)

    @domain_router.delete("/{domain}")
    async def delete_domain(
        self,
        domain: models.Domain = Depends(path_domain),
        checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
    ):
        # TODO: delete repository, add lock
        domain.delete()
        return IsSuccess()

    @domain_router.get("/{domain}")
    async def get_domain(
        self,
        background_tasks: BackgroundTasks,
        domain: models.Domain = Depends(path_domain),
        checker: Any = Depends(PermissionChecker(PermissionType.READ)),
    ) -> schemas.Domain:
        # for debug purpose
        background_tasks.add_task(self.create_domain_background, domain)
        return schemas.Domain.from_orm(domain)

    @domain_router.get("/{domain}/init")
    async def init_domain(
        self,
        domain: models.Domain = Depends(path_domain),
        checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
    ):
        await self.initialize_domain_background(domain)


@cbv(domain_router)
class DomainUploadRoute:
    auth_logic: Callable = Depends(dependency_supplier.auth_logic)
    graphdb: GraphDB = Depends(get_graphdb)

    @domain_router.post(
        "/{domain}/upload",
        status_code=200,
        response_model=IsSuccess,
        description="Upload a Turtle file. An example file: https://gitlab.com/jbkoh/brick-server-dev/blob/dev/examples/data/bldg.ttl",
        summary="Uplaod a Turtle file",
    )
    async def upload(
        self,
        background_tasks: BackgroundTasks,
        domain: models.Domain = Depends(path_domain),
        file: UploadFile = File(...),
        checker: Any = Depends(PermissionChecker(PermissionType.WRITE)),
    ):
        await self.graphdb.clear_import_file(domain.name, file.filename)
        background_tasks.add_task(
            self.graphdb.import_schema_from_file, domain.name, file, delete=False
        )
        # await self.graphdb.import_schema_from_file(file, named_graph, delete=True)
        return IsSuccess()
