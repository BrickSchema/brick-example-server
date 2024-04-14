from brick_server.minimal.config.settings.base import BackendBaseSettings
from brick_server.minimal.config.settings.environment import Environment


class BackendStageSettings(BackendBaseSettings):
    DESCRIPTION: str | None = "Test Environment."
    DEBUG: bool = True
    ENVIRONMENT: Environment = Environment.STAGING
