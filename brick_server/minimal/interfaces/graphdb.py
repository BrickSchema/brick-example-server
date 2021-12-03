import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from fastapi import UploadFile
from loguru import logger


class GraphDB:
    def __init__(self, host: str, port: int, repository: str) -> None:
        self.host = host
        self.port = port
        self.base_url = f"http://{self.host}:{self.port}/"
        self.repository = repository
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def init_repository(self):
        logger.info("GraphDB init repository")
        data = {"id": self.repository, "type": "free", "title": "", "params": {}}
        resp = await self.client.post("/rest/repositories", json=data)
        if resp.status_code != 201:
            logger.debug(resp.content)
        # resp = await self.client.get(f"/rest/repositories/{self.repository}/size")
        # logger.debug(resp.content)

    def generate_import_settings(self, name: str, named_graph: str):
        return {
            "type": "url",
            "name": name,
            "format": "",
            "data": name,
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

    async def check_schema(self, name: str) -> bool:
        resp = await self.client.get(
            f"/rest/data/import/upload/{self.repository}", timeout=30
        )
        data = resp.json()
        for row in data:
            if row.get("name", None) == name:
                if row.get("status", None) == "DONE":
                    return True
                return False
        return False

    async def import_schema_from_url(self, url: str, named_graph: Optional[str] = None):
        logger.info("GraphDB import Brick Schema from url {}", url)
        if not named_graph:
            named_graph = url
        data = self.generate_import_settings(url, named_graph)
        resp = await self.client.post(
            f"/rest/data/import/upload/{self.repository}/url", json=data, timeout=30
        )
        logger.debug(resp.content)

    async def import_schema_from_file(
        self, file: UploadFile, named_graph: Optional[str] = None
    ):
        if not named_graph:
            named_graph = Path(file.filename).stem + ":"
        data = self.generate_import_settings(file.filename, named_graph)
        logger.info(
            "GraphDB import Brick Schema from file {} as {}", file.filename, named_graph
        )
        files = {
            "file": (file.filename, file.file, "application/octet-stream"),
            "importSettings": ("blob", json.dumps(data), "application/json"),
        }
        resp = await self.client.post(
            f"/rest/data/import/upload/{self.repository}/file", files=files
        )
        logger.debug(resp.content)

    async def query(
        self, query_str: str, is_update=False, limit: int = 1000, offset: int = 0
    ):
        resp = await self.client.post(
            "/rest/sparql/addKnownPrefixes",
            data=query_str,
            headers={
                "X-GraphDB-Repository": self.repository,
            },
        )
        query_str = resp.content.decode("utf-8")
        query_str = ast.literal_eval(query_str)
        logger.debug(query_str)
        data = {
            "query": query_str,
            "infer": True,
            "saveAs": True,
            "offset": offset,
            "limit": limit,
        }
        headers = {
            "Accept": "application/x-sparqlstar-results+json, application/sparql-results+json"
        }
        if is_update:
            resp = await self.client.get(
                f"/repositories/{self.repository}", params=data, headers=headers
            )
        else:
            resp = await self.client.post(
                f"/repositories/{self.repository}", data=data, headers=headers
            )
        result = resp.json()
        logger.debug(result)
        return result
