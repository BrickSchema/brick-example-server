import pytest

from .common import DOMAIN_BASE, EXAMPLES_DATA_FOLDER, TEST_DOMAIN_NAME
from .utils import ensure_graphdb_upload


@pytest.mark.asyncio
async def test_domain_create(domain):
    assert domain.name == TEST_DOMAIN_NAME


@pytest.mark.asyncio
@pytest.mark.depends(on=["test_domain_create"])
async def test_domain_upload(graphdb, client, admin_headers):
    with open(EXAMPLES_DATA_FOLDER / "bldg.ttl", "rb") as fp:
        files = {
            "file": ("bldg.ttl", fp, "application/octet-stream"),
        }
        resp = await client.post(
            f"{DOMAIN_BASE}/{TEST_DOMAIN_NAME}/upload",
            headers=admin_headers,
            files=files,
            follow_redirects=False,
        )
        assert resp.status_code == 200
        await ensure_graphdb_upload(graphdb, TEST_DOMAIN_NAME, "bldg.ttl")
