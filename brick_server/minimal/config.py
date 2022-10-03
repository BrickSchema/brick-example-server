from typing import Type, Union

from fastapi_rest_framework import config


@config.add
class BaseConfig(config.Base):
    """
    Server configuration

    The configuration of server connection, debug mode and proxy
    """

    debug: bool = False
    host: str = "localhost"
    port: int = 9000
    workers: int = 4

    default_brick_url: str = "https://brickschema.org/schema/Brick"

    hostname: str = "http://localhost:9000"
    frontend: str = "DUMMY-NOT-WORK"


@config.add
class AuthConfig(config.Base):
    """
    Auth configuration

    The configuration of JWT, OAuth
    """

    # jwt config
    jwt_secret: str = "secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_seconds: int = 14 * 24 * 60 * 60  # 14 days, in seconds

    # oauth config


@config.add
class DatabaseConfig(config.Base):
    """
    Database configuration
    """

    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_username: str = ""
    mongo_password: str = ""
    mongo_dbname: str = "brickserver"

    timescale_host: str = "localhost"
    timescale_port: int = 5432
    timescale_username: str = "bricker"
    timescale_password: str = "brick-demo"
    timescale_dbname: str = "brick"

    brick_host: str = "localhost"
    brick_port: int = 8890
    brick_api_endpoint: str = "sparql"
    brick_version: str = "1.1"
    brick_base_ns: str = "bldg:"
    brick_base_graph: str = "brick-base-graph"

    graphdb_host: str = "localhost"
    graphdb_port: int = 7200
    graphdb_repository: str = "brickserver"

    grafana_host: str = "localhost"
    grafana_port: int = 3000
    grafana_api_endpoint: str = "api"
    grafana_api_key: str = "YOUR_API_TOKEN"


FastAPIConfig: Type[
    Union[BaseConfig, AuthConfig, DatabaseConfig]
] = config.generate_config_class(mixins=[config.EnvFileMixin, config.CLIMixin])
