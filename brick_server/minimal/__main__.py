import click
import uvicorn
from click_default_group import DefaultGroup

from brick_server.minimal.config.manager import settings


@click.group(cls=DefaultGroup, default="serve", default_if_no_args=True)
@click.help_option("--help", "-h")
def cli_group():
    pass


@click.command()
def serve() -> None:
    uvicorn.run(
        app="brick_server.minimal.app:backend_app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.SERVER_WORKERS and settings.DEBUG,
        reload_dirs=["brick_server/minimal"],
        workers=settings.SERVER_WORKERS,
        log_level=settings.LOGGING_LEVEL,
    )


# @click.command("openapi")
# @click.option("-o", "--output", type=click.Path(), required=False, default=None)
# def main(output: Optional[str]) -> None:
#     openapi_json = json.dumps(app.openapi(), indent=2)
#     if output is None:
#         print(openapi_json)
#     else:
#         with Path(output).open("w", encoding="utf-8") as f:
#             f.write(openapi_json)


@click.command()
@click.option("--user-id", type=str, default="admin")
@click.option("--app-name", type=str, default="")
@click.option("--domain", type=str, default="")
@click.option("--token-lifetime", type=int, default=0)
@click.option("--create-user", is_flag=True)
def generate_jwt(
    user_id: str, app_name: str, domain: str, token_lifetime: int, create_user: bool
) -> None:
    from brick_server.minimal.auth.authorization import create_user
    from brick_server.minimal.auth.jwt import create_jwt_token
    from brick_server.minimal.dbs import mongo_connection
    from brick_server.minimal.models import User, get_doc_or_none

    _ = mongo_connection  # prevent import removed by pycln
    if token_lifetime == 0:
        token_lifetime = settings.JWT_EXPIRE_SECONDS

    user = get_doc_or_none(User, user_id=user_id)
    if create_user and user is None:
        user = create_user(name=user_id, user_id=user_id, email=f"{user_id}@gmail.com")
    jwt = create_jwt_token(
        user_id=user_id, app_name=app_name, domain=domain, token_lifetime=token_lifetime
    )
    print(jwt)


if __name__ == "__main__":
    cli_group.add_command(serve)
    cli_group.add_command(generate_jwt)
    cli_group()
