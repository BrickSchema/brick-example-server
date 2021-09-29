from datetime import datetime
from typing import Optional

import httpx
from loguru import logger


class GraphDB:
    def __init__(self, host: str, port: int, repository: str) -> None:
        self.host = host
        self.port = port
        self.base_url = f"http://{self.host}:{self.port}/"
        self.repository = repository

    async def init_repository(self):
        logger.info("GraphDB init repository")
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            data = {"id": self.repository, "type": "free", "title": "", "params": {}}
            resp = await client.post("/rest/repositories", json=data)
            if resp.status_code != 201:
                logger.debug(resp.content)

    async def import_schema_from_url(self, url: str, named_graph: Optional[str] = None):
        logger.info("GraphDB init Brick Schema {}", url)
        if named_graph is None:
            named_graph = url
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            data = {
                "type": "url",
                "name": url,
                "format": "",
                "data": url,
                "status": "NONE",
                "message": "",
                "context": named_graph,
                "replaceGraphs": [named_graph],
                "baseURI": None,
                "forceSerial": False,
                "timestamp": int(datetime.utcnow().timestamp() * 1000),
                "parserSettings": {
                    "preserveBNodeIds": False,
                    "failOnUnknownDataTypes": False,
                    "verifyDataTypeValues": False,
                    "normalizeDataTypeValues": False,
                    "failOnUnknownLanguageTags": False,
                    "verifyLanguageTags": True,
                    "normalizeLanguageTags": False,
                    "stopOnError": True,
                },
                "requestIdHeadersToForward": None,
            }
            resp = await client.post(
                f"/rest/data/import/upload/{self.repository}/url", json=data
            )
            logger.debug(resp.content)
