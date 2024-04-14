import typing

import fastapi
import loguru

from brick_server.minimal.interfaces.mongodb import initialize_mongodb
from brick_server.minimal.interfaces.timeseries import (
    dispose_timeseries,
    initialize_timeseries,
)


def execute_backend_server_event_handler(backend_app: fastapi.FastAPI) -> typing.Any:
    async def launch_backend_server_events() -> None:
        await initialize_mongodb(backend_app=backend_app)
        await initialize_timeseries()

    return launch_backend_server_events


def terminate_backend_server_event_handler(backend_app: fastapi.FastAPI) -> typing.Any:
    @loguru.logger.catch
    async def stop_backend_server_events() -> None:
        await dispose_timeseries()

    return stop_backend_server_events
