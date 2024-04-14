from brick_server.minimal.config.settings.base import BackendBaseSettings
from brick_server.minimal.config.settings.environment import Environment


class BackendDevSettings(BackendBaseSettings):
    DESCRIPTION: str | None = "Development Environment."
    DEBUG: bool = True
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
