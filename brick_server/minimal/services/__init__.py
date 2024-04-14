from fastapi import APIRouter
from starlette.responses import RedirectResponse

from brick_server.minimal.config.manager import settings
from brick_server.minimal.services.actuation import router as actuation_router
from brick_server.minimal.services.auth import router as auth_router
from brick_server.minimal.services.data import router as data_router
from brick_server.minimal.services.domain import router as domain_router
from brick_server.minimal.services.user import router as user_router

router = APIRouter()


@router.get("/", include_in_schema=False)
def redirect_docs():
    return RedirectResponse(url=settings.DOCS_URL)


router.include_router(router=auth_router)
router.include_router(router=user_router)
router.include_router(router=domain_router)
router.include_router(router=actuation_router)
router.include_router(router=data_router)
