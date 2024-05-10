import logging
import pathlib

import decouple
import pydantic
import pydantic_settings

ROOT_DIR: pathlib.Path = pathlib.Path(
    __file__
).parent.parent.parent.parent.parent.resolve()


class BackendBaseSettings(pydantic_settings.BaseSettings):
    TITLE: str = "Brick Server Minimal"
    VERSION: str = "0.1.0"
    TIMEZONE: str = "UTC"
    DESCRIPTION: str = ""
    DEBUG: bool = False
    CACHE: bool = decouple.config("CACHE", cast=bool, default=True)

    # brick
    BRICK_VERSION: str = decouple.config("BRICK_VERSION", cast=str, default="1.3")
    DEFAULT_BRICK_URL: str = decouple.config(
        "DEFAULT_BRICK_URL", cast=str, default="https://brickschema.org/schema/Brick"
    )
    DEFAULT_REF_SCHEMA_URL: str = decouple.config(
        "DEFAULT_REF_SCHEMA_URL",
        cast=str,
        default="https://gist.githubusercontent.com/tc-imba/714c2043e893b1538406a9113140a4fe/"
        "raw/2fa8df840f3e4f1deb647b14fe524976f004e321/ref-schema.ttl",
    )

    # backend
    SERVER_HOST: str = decouple.config("SERVER_HOST", cast=str, default="0.0.0.0")
    SERVER_PORT: int = decouple.config("SERVER_PORT", cast=int, default=9000)
    SERVER_WORKERS: int = decouple.config("SERVER_WORKERS", cast=int, default=1)
    API_PREFIX: str = "/brickapi/v1"
    DOCS_URL: str = "/brickapi/v1/docs"
    OPENAPI_URL: str = "/brickapi/v1/openapi.json"
    REDOC_URL: str = "/brickapi/v1/redoc"
    OPENAPI_PREFIX: str = ""
    FRONTEND_URL: str = decouple.config("FRONTEND_URL", cast=str, default=DOCS_URL)

    # mongo
    MONGO_HOST: str = decouple.config("MONGO_HOST", cast=str, default="localhost")
    MONGO_PORT: int = decouple.config("MONGO_PORT", cast=int, default=27017)
    MONGO_SCHEMA: str = decouple.config("MONGO_SCHEMA", cast=str, default="mongodb")
    MONGO_DATABASE: str = decouple.config(
        "MONGO_DATABASE", cast=str, default="brickserver"
    )
    MONGO_USERNAME: str = decouple.config("MONGO_USERNAME", cast=str, default="")
    MONGO_PASSWORD: str = decouple.config("MONGO_PASSWORD", cast=str, default="")

    # timescaledb
    TIMESCALE_HOST: str = decouple.config(
        "TIMESCALE_HOST", cast=str, default="localhost"
    )
    TIMESCALE_PORT: int = decouple.config("TIMESCALE_PORT", cast=int, default=5432)
    TIMESCALE_USERNAME: str = decouple.config(
        "TIMESCALE_USERNAME", cast=str, default="bricker"
    )
    TIMESCALE_PASSWORD: str = decouple.config(
        "TIMESCALE_PASSWORD", cast=str, default="brick-demo"
    )
    TIMESCALE_DATABASE: str = decouple.config(
        "TIMESCALE_DATABASE", cast=str, default="brick"
    )

    # influxdb
    INFLUXDB_URL: str = decouple.config(
        "INFLUXDB_URL",
        cast=str,
        default="https://us-east-1-1.aws.cloud2.influxdata.com",
    )
    INFLUXDB_TOKEN: str = decouple.config("INFLUXDB_TOKEN", cast=str, default="")
    INFLUXDB_ORG: str = decouple.config(
        "INFLUXDB_ORG", cast=str, default="9d4d3af8fd50fcbb"
    )
    INFLUXDB_BUCKET: str = decouple.config(
        "INFLUXDB_BUCKET", cast=str, default="CO2-Exp"
    )

    # redis
    REDIS_HOST: str = decouple.config("TIMESCALE_HOST", cast=str, default="localhost")
    REDIS_PORT: int = decouple.config("REDIS_PORT", cast=int, default=6379)
    REDIS_PASSWORD: str = decouple.config(
        "REDIS_PASSWORD", cast=str, default="brick-demo"
    )
    REDIS_DATABASE: int = decouple.config("REDIS_DATABASE", cast=int, default=0)

    # graphdb
    GRAPHDB_HOST: str = decouple.config("GRAPHDB_HOST", cast=str, default="localhost")
    GRAPHDB_PORT: int = decouple.config("GRAPHDB_PORT", cast=int, default=7200)
    GRAPHDB_REPOSITORY: str = decouple.config(
        "GRAPHDB_REPOSITORY", cast=str, default="brickserver"
    )

    # # db
    # DB_MAX_POOL_CON: int = decouple.config("DB_MAX_POOL_CON", cast=int, default=5)  # type: ignore
    # DB_POOL_SIZE: int = decouple.config("DB_POOL_SIZE", cast=int, default=100)  # type: ignore
    # DB_POOL_OVERFLOW: int = decouple.config("DB_POOL_OVERFLOW", cast=int, default=80)  # type: ignore
    # DB_TIMEOUT: int = decouple.config("DB_TIMEOUT", cast=int, default=20)  # type: ignore
    # IS_DB_ECHO_LOG: bool = decouple.config("IS_DB_ECHO_LOG", cast=bool, default=False)  # type: ignore
    # IS_DB_FORCE_ROLLBACK: bool = decouple.config("IS_DB_FORCE_ROLLBACK", cast=bool, default=True)  # type: ignore
    # IS_DB_EXPIRE_ON_COMMIT: bool = decouple.config("IS_DB_EXPIRE_ON_COMMIT", cast=bool, default=True)  # type: ignore
    #
    # # s3
    # S3_HOST: str = decouple.config("S3_HOST", cast=str, default="127.0.0.1")  # type: ignore
    # S3_PORT: int = decouple.config("S3_PORT", cast=int, default=9000)  # type: ignore
    # S3_USERNAME: str = decouple.config("S3_USERNAME", cast=str, default="minioadmin")  # type: ignore
    # S3_PASSWORD: str = decouple.config("S3_PASSWORD", cast=str, default="minioadmin")  # type: ignore
    # S3_BUCKET: str = decouple.config("S3_BUCKET", cast=str, default="brick")  # type: ignore
    # S3_PUBLIC_URL: str = decouple.config("S3_PUBLIC_URL", cast=str, default="http://localhost:9000")  # type: ignore

    # auth
    API_TOKEN: str = decouple.config("API_TOKEN", cast=str, default="YOUR-API-TOKEN")  # type: ignore
    AUTH_TOKEN: str = decouple.config("AUTH_TOKEN", cast=str, default="YOUR-AUTHENTICATION-TOKEN")  # type: ignore
    JWT_SECRET_KEY: str = decouple.config("JWT_SECRET_KEY", cast=str, default="YOUR-JWT-SECRET-KEY")  # type: ignore
    JWT_SUBJECT: str = decouple.config("JWT_SUBJECT", cast=str, default="brick")  # type: ignore
    JWT_TOKEN_PREFIX: str = decouple.config("JWT_TOKEN_PREFIX", cast=str, default="brick")  # type: ignore
    JWT_ALGORITHM: str = decouple.config("JWT_ALGORITHM", cast=str, default="HS256")  # type: ignore
    JWT_MIN: int = decouple.config("JWT_MIN", cast=int, default=0)  # type: ignore
    JWT_HOUR: int = decouple.config("JWT_HOUR", cast=int, default=0)  # type: ignore
    JWT_DAY: int = decouple.config("JWT_DAY", cast=int, default=14)  # type: ignore
    JWT_EXPIRE_SECONDS: int = ((JWT_DAY * 24 + JWT_HOUR) * 60 + JWT_MIN) * 60

    # oauth
    OAUTH_GOOGLE_CLIENT_ID: str = decouple.config(
        "OAUTH_GOOGLE_CLIENT_ID", cast=str, default=""
    )
    OAUTH_GOOGLE_CLIENT_SECRET: str = decouple.config(
        "OAUTH_GOOGLE_CLIENT_SECRET", cast=str, default=""
    )

    JAAS_APP_ID: str = decouple.config("JAAS_APP_ID", cast=str, default="YOUR-JAAS-APP-ID")  # type: ignore
    JAAS_API_KEY: str = decouple.config("JAAS_API_KEY", cast=str, default="YOUR-JAAS-API-KEY")  # type: ignore
    JAAS_PRIVATE_KEY_PATH: str = decouple.config(
        "JAAS_PRIVATE_KEY_PATH", cast=str, default="YOUR-JAAS-PRIVATE-KEY-PATH"
    )  # type: ignore
    IS_ALLOWED_CREDENTIALS: bool = decouple.config("IS_ALLOWED_CREDENTIALS", cast=bool, default=True)  # type: ignore
    HASHING_ALGORITHM_LAYER_1: str = decouple.config(
        "HASHING_ALGORITHM_LAYER_1", cast=str, default="bcrypt"
    )  # type: ignore
    HASHING_ALGORITHM_LAYER_2: str = decouple.config(
        "HASHING_ALGORITHM_LAYER_2", cast=str, default="argon2"
    )  # type: ignore
    HASHING_SALT: str = decouple.config("HASHING_SALT", cast=str, default="YOUR-RANDOM-SALTY-SALT")  # type: ignore

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",  # React default port
        "http://0.0.0.0:3000",
        "http://127.0.0.1:3000",  # React docker port
        "http://127.0.0.1:3001",
        "http://localhost:5173",  # Qwik default port
        "http://0.0.0.0:5173",
        "http://127.0.0.1:5173",  # Qwik docker port
        "http://127.0.0.1:5174",
    ]
    ALLOWED_METHODS: list[str] = ["*"]
    ALLOWED_HEADERS: list[str] = ["*"]

    LOGGING_LEVEL: int = logging.INFO
    LOGGERS: tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    class Config(pydantic.BaseConfig):
        case_sensitive: bool = True
        env_file: str = f"{str(ROOT_DIR)}/.env"
        validate_assignment: bool = True
        extra: str = "allow"

    @property
    def set_backend_app_attributes(self) -> dict[str, str | bool | dict | None]:
        """
        Set all `FastAPI` class' attributes with the custom values defined in `BackendBaseSettings`.
        """
        return {
            "title": self.TITLE,
            "version": self.VERSION,
            "debug": self.DEBUG,
            "description": self.DESCRIPTION,
            "docs_url": self.DOCS_URL,
            "openapi_url": self.OPENAPI_URL,
            "redoc_url": self.REDOC_URL,
            "openapi_prefix": self.OPENAPI_PREFIX,
            "api_prefix": self.API_PREFIX,
            "swagger_ui_parameters": {"docExpansion": "none"},
        }
