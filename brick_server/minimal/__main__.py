import click
import uvicorn
from click_default_group import DefaultGroup
from fastapi_rest_framework import cli, config

from brick_server.minimal.config import FastAPIConfig


@click.group(cls=DefaultGroup, default="serve", default_if_no_args=True)
@click.help_option("--help", "-h")
def cli_group():
    pass


@cli.command()
def serve() -> None:
    settings = config.init_settings(FastAPIConfig)
    uvicorn.run(
        "brick_server.minimal.app:app",
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
        reload=settings.debug,
        log_level="debug",
        reload_dirs=["brick_server/minimal"],
        workers=settings.workers,
    )


@cli.command()
@click.option("--user-id", type=str, default="admin")
@click.option("--app-name", type=str, default="")
@click.option("--token-lifetime", type=int, default=0, help="use ")
def generate_jwt(user_id: str, app_name: str, token_lifetime: int) -> None:
    settings = config.init_settings(FastAPIConfig)

    from brick_server.minimal.auth.jwt import create_jwt_token

    if token_lifetime == 0:
        token_lifetime = settings.jwt_expire_seconds

    jwt = create_jwt_token(
        user_id=user_id, app_name=app_name, token_lifetime=token_lifetime
    )
    print(jwt)


if __name__ == "__main__":
    cli_group.add_command(serve)
    cli_group.add_command(generate_jwt)
    cli_group()
