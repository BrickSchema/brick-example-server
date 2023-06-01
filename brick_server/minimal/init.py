import asyncpg
from loguru import logger

from brick_server.minimal.dbs import ts_db


async def initialization() -> None:
    # await graphdb.init_repository()
    # graphs = await graphdb.list_graphs()
    # if settings.default_brick_url in graphs:
    #     logger.info("GraphDB Brick Schema found.")
    # else:
    #     logger.info("GraphDB Brick Schema not found.")
    #     await graphdb.import_schema_from_url(settings.default_brick_url)
    # logger.info("Brick SPARQL load schema")
    # await brick_sparql.load_schema()

    try:
        logger.info("Init timescale tables")
        await ts_db.init()
    except asyncpg.exceptions.DuplicateTableError:
        logger.info("Timescale tables have been already created.")
