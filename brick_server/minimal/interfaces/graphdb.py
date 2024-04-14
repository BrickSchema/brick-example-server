import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from fastapi import UploadFile
from loguru import logger

from brick_server.minimal.config.manager import settings
from brick_server.minimal.utilities.exceptions import BizError, ErrorCode


class GraphDB:
    def __init__(self, host: str, port: int, repository: str) -> None:
        self.host = host
        self.port = port
        self.base_url = f"http://{self.host}:{self.port}/"
        # self.repository = repository
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def init_repository(self, repository):
        logger.info("GraphDB init repository")
        data = {
            "id": repository,
            "type": "free",
            "title": "",
            "params": {
                "ruleset": {
                    "label": "Ruleset",
                    "name": "ruleset",
                    "value": "owl2-rl-optimized",
                }
            },
        }
        resp = await self.client.post("/rest/repositories", json=data, timeout=30)
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

    async def check_import_schema(self, repository: str, name: str) -> bool:
        resp = await self.client.get(
            f"/rest/data/import/upload/{repository}", timeout=30
        )
        data = resp.json()
        for row in data:
            if row.get("name", None) == name:
                if row.get("status", None) == "DONE":
                    return True
                return False
        return False

    async def list_graphs(self, repository):
        resp = await self.client.get(
            f"/repositories/{repository}/contexts",
            headers={"Accept": "application/json"},
            timeout=30,
        )
        try:
            data = resp.json()
            logger.info(data)
            result = data["results"]["bindings"]
            graphs = list(map(lambda x: x["contextID"]["value"], result))
            logger.info(graphs)
            return graphs
        except Exception as e:
            logger.exception(e)
            return []

    async def clear_import_file(self, repository: str, file_name: str):
        logger.info("GraphDB clear import {}", file_name)
        resp = await self.client.request(
            "DELETE",
            f"/rest/data/import/upload/{repository}/status",
            params={"remove": "true"},
            json=[file_name],
        )
        logger.debug(resp.request)
        logger.debug(resp.content)

    async def delete_schema(self, repository: str, named_graph: str):
        logger.info("GraphDB delete schema {}", named_graph)
        resp = await self.client.post(
            f"/repositories/{repository}/statements",
            headers={"Accept": "application/json"},
            data={"update": f"CLEAR GRAPH <{named_graph}>"},
            timeout=300,
        )
        logger.debug(resp.content)

    async def import_schema_from_url(
        self,
        repository: str,
        url: str,
        named_graph: Optional[str] = None,
        delete: bool = False,
    ):
        logger.info("GraphDB import schema from url {}", url)
        if not named_graph:
            named_graph = url
        if delete:
            await self.delete_schema(repository, named_graph)
        data = self.generate_import_settings(url, named_graph)
        resp = await self.client.post(
            f"/rest/data/import/upload/{repository}/url", json=data, timeout=30
        )
        logger.debug(resp.content)

    async def import_schema_from_file(
        self,
        repository: str,
        file: UploadFile,
        named_graph: Optional[str] = None,
        delete: bool = False,
    ):
        if not named_graph:
            named_graph = Path(file.filename).stem + ":"
        if delete:
            await self.delete_schema(repository, named_graph)
        data = self.generate_import_settings(file.filename, named_graph)
        logger.info(
            "GraphDB import Brick Schema from file {} as {}", file.filename, named_graph
        )
        files = {
            "file": (file.filename, file.file, "application/octet-stream"),
            "importSettings": (
                "blob",
                json.dumps(data).encode("utf-8"),
                "application/json",
            ),
        }
        resp = await self.client.post(
            f"/rest/data/import/upload/{repository}/file", files=files
        )
        logger.debug(resp.content)

    async def query(
        self,
        repository: str,
        query_str: str,
        is_update=False,
        limit: int = 10000,
        offset: int = 0,
    ):
        resp = await self.client.post(
            "/rest/sparql/addKnownPrefixes",
            data=query_str,
            headers={
                "X-GraphDB-Repository": repository,
            },
        )
        query_str = resp.content.decode("utf-8")
        query_str = ast.literal_eval(query_str)
        # logger.debug(query_str)
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
                f"/repositories/{repository}", params=data, headers=headers
            )
        else:
            resp = await self.client.post(
                f"/repositories/{repository}", data=data, headers=headers
            )
        if resp.status_code != 200:
            raise BizError(
                ErrorCode.GraphDBError,
                resp.content.decode("utf-8"),
            )
        result = resp.json()
        # logger.debug(result)
        return result


graphdb = GraphDB(
    host=settings.GRAPHDB_HOST,
    port=settings.GRAPHDB_PORT,
    repository=settings.GRAPHDB_REPOSITORY,
)
