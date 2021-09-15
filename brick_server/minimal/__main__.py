import uvicorn
from fastapi_rest_framework import cli, config

from brick_server.minimal.config import FastAPIConfig


@cli.command()
def main() -> None:
    settings = config.init_settings(FastAPIConfig)
    uvicorn.run(
        "brick_server.minimal.app:app",
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
        reload=settings.debug,
        log_level="debug",
        # reload_dirs=["brick_server"],
    )


if __name__ == "__main__":
    main()
