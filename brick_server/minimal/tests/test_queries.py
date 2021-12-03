import pytest

from .common import ENTITY_BASE, QUERY_BASE
from .utils import ensure_graphdb_upload


@pytest.mark.asyncio
async def test_load_ttl(graphdb, client, admin_headers):
    with open("examples/data/bldg.ttl", "rb") as fp:
        # admin_headers.update({"Content-Type": "text/turtle"})
        files = {
            "file": ("bldg.ttl", fp, "application/octet-stream"),
        }
        resp = await client.post(
            ENTITY_BASE + "/upload",
            headers=admin_headers,
            files=files,
            allow_redirects=False,
        )
        assert resp.status_code == 200
        await ensure_graphdb_upload(graphdb, "bldg.ttl")


@pytest.mark.asyncio
@pytest.mark.depends(on=["test_load_ttl"])
async def test_simple_sparql(client, admin_headers):
    qstr = """
select ?s where {
  ?s a brick:Zone_Air_Temperature_Sensor.
}
"""
    admin_headers.update({"Content-Type": "sparql-query"})
    resp = await client.post(QUERY_BASE + "/sparql", data=qstr, headers=admin_headers)
    print(resp.json())
    assert resp.json()["results"]["bindings"]


@pytest.mark.asyncio
@pytest.mark.depends(on=["test_load_ttl"])
async def test_simple_sql(client, admin_headers):
    qstr = """
select * from brick_data LIMIT 10;
"""
    admin_headers.update({"Content-Type": "application/sql"})
    resp = await client.post(
        QUERY_BASE + "/timeseries", data=qstr, headers=admin_headers
    )
    assert resp.status_code == 200
    assert resp.json()


@pytest.mark.asyncio
@pytest.mark.depends(on=["test_load_ttl"])
async def test_sparql_equip_tree(client, admin_headers):
    qstr = """
select ?child ?parent where {
    {?parent brick:hasPart ?child.}
    UNION
    {?child brick:isPartOf ?parent.}
    UNION
    {?parent brick:feeds ?child.}
    UNION
    {?child brick:isFedBy ?parent.}
    ?parent a/rdfs:subClassOf* brick:Equipment.
    ?child a/rdfs:subClassOf* brick:Equipment.
}
"""
    admin_headers.update({"Content-Type": "sparql-query"})
    resp = await client.post(QUERY_BASE + "/sparql", data=qstr, headers=admin_headers)
    assert len(resp.json()["results"]["bindings"]) > 2


@pytest.mark.asyncio
@pytest.mark.depends(on=["test_load_ttl"])
async def test_sparql_location_tree(client, admin_headers):
    qstr = """
select ?parent ?child where {
  ?parent a/rdfs:subClassOf brick:Location.
  ?child brick:isPartOf+ ?parent.
}
"""
    admin_headers.update({"Content-Type": "sparql-query"})
    resp = await client.post(QUERY_BASE + "/sparql", data=qstr, headers=admin_headers)
    assert len(resp.json()["results"]["bindings"]) > 4
