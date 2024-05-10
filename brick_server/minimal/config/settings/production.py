import decouple

from brick_server.minimal.config.settings.base import BackendBaseSettings
from brick_server.minimal.config.settings.environment import Environment


class BackendProdSettings(BackendBaseSettings):
    DESCRIPTION: str | None = "Production Environment."
    ENVIRONMENT: Environment = Environment.PRODUCTION

    SERVER_WORKERS: int = decouple.config("SERVER_WORKERS", cast=int, default=4)
