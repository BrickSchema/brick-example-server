import pytest

from .common import ENTITY_BASE, EXAMPLES_DATA_FOLDER
from .utils import ensure_graphdb_upload


@pytest.mark.asyncio
async def test_load_ttl(graphdb, client, admin_headers):
    with open(EXAMPLES_DATA_FOLDER / "ebu3b_brick.ttl", "rb") as fp:
        files = {
            "file": ("ebu3b.ttl", fp, "application/octet-stream"),
        }
        resp = await client.post(
            ENTITY_BASE + "/upload",
            params={"named_graph": "http://ucsd.edu/building/ontology/ebu3b#"},
            headers=admin_headers,
            files=files,
            follow_redirects=False,
        )
        assert resp.status_code == 200
        await ensure_graphdb_upload(graphdb, "ebu3b.ttl")


@pytest.mark.asyncio
@pytest.mark.depends(on=["test_load_ttl"])
async def test_get_an_entity(client, admin_headers):
    # resp = requests.get(ENTITY_BASE + '/' + quote_plus(znt_id), headers=headers)
    resp = await client.get(
        ENTITY_BASE,
        headers=admin_headers,
        params={
            "entity_id": "http://ucsd.edu/building/ontology/ebu3b#EBU3B_HVAC_Zone_Rm_3207"
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "Zone" in resp.json()["type"].split("#")
    # How to reuse the response schema?


# def test_reload_ttl():
#     headers = authorize_headers({
#         'Content-Type': 'text/turtle',
#     })
#     with open('examples/data/bldg.ttl', 'rb') as fp:
#         resp = requests.post(ENTITY_BASE + '/upload',
#                              headers=headers,
#                              data=fp,
#                              follow_redirects=False,
#                              )
#         assert resp.status_code == 200


@pytest.mark.asyncio
@pytest.mark.depends(on=["test_load_ttl"])
async def test_get_all_entities(client, admin_headers):
    resp = await client.post(
        ENTITY_BASE + "/list",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["entity_ids"]


@pytest.mark.asyncio
@pytest.mark.depends(on=["test_load_ttl"])
async def test_get_entities_by_relation(client, admin_headers):
    resp = await client.post(
        ENTITY_BASE + "/list",
        headers=admin_headers,
        json={"feeds": ["ebu3b:EBU3B_HVAC_Zone_Rm_3207"]},
    )
    assert resp.status_code == 200
    assert resp.json()["entity_ids"] == [
        "http://ucsd.edu/building/ontology/ebu3b#EBU3B_VAV_Rm_3207"
    ]
