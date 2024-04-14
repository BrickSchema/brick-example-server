import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi_restful.timing import add_timing_middleware
from loguru import logger

from brick_server.minimal.config.errors import register_error_handlers
from brick_server.minimal.config.events import (
    execute_backend_server_event_handler,
    terminate_backend_server_event_handler,
)
from brick_server.minimal.config.manager import settings
from brick_server.minimal.securities.auth import default_auth_logic
from brick_server.minimal.utilities.dependencies import update_dependency_supplier
from brick_server.minimal.utilities.logging import init_logging, intercept_all_loggers

update_dependency_supplier(default_auth_logic)


def initialize_backend_application() -> fastapi.FastAPI:
    init_logging()
    intercept_all_loggers()
    app = fastapi.FastAPI(**settings.set_backend_app_attributes)  # type: ignore

    add_timing_middleware(app, record=logger.info)
    app.logger = logger

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=settings.IS_ALLOWED_CREDENTIALS,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )

    app.add_event_handler(
        "startup",
        execute_backend_server_event_handler(backend_app=app),
    )
    app.add_event_handler(
        "shutdown",
        terminate_backend_server_event_handler(backend_app=app),
    )

    register_error_handlers(app)

    from brick_server.minimal.services import router as api_endpoint_router

    app.include_router(router=api_endpoint_router, prefix=settings.API_PREFIX)

    return app


backend_app: fastapi.FastAPI = initialize_backend_application()
