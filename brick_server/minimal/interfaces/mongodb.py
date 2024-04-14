from typing import Type

import fastapi
import pydantic
from beanie import Document, init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorChangeStream, AsyncIOMotorClient

from brick_server.minimal import models
from brick_server.minimal.config.manager import settings


class AsyncDatabase:
    def __init__(self):
        self.mongo_uri: pydantic.MongoDsn = pydantic.MongoDsn(
            url=f"{settings.MONGO_SCHEMA}://{settings.MONGO_USERNAME}:{settings.MONGO_PASSWORD}@{settings.MONGO_HOST}:{settings.MONGO_PORT}",
        )
        self.async_client: AsyncIOMotorClient = AsyncIOMotorClient(
            str(self.mongo_uri), uuidRepresentation="standard"
        )
        self.async_database: AsyncIOMotorChangeStream = self.async_client[
            settings.MONGO_DATABASE
        ]


async_db: AsyncDatabase = AsyncDatabase()


async def initialize_mongodb(backend_app: fastapi.FastAPI) -> None:
    logger.info("Database Connection --- Establishing . . .")

    backend_app.state.db = async_db

    server_info = await async_db.async_client.server_info()
    logger.info("Database Version: MongoDB v{}", server_info["version"])
    document_models: list[Type[Document]] = [
        models.User,
        models.Domain,
    ]
    await init_beanie(
        database=async_db.async_database,
        document_models=document_models,
    )
    logger.info(
        "Init collections: {}",
        ", ".join([model.get_settings().name for model in document_models]),
    )
    logger.info("Database Connection --- Successfully Established!")
