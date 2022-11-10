import pytest

from .common import QUERY_BASE


@pytest.mark.asyncio
@pytest.mark.depends(on=["tests/test_domain.py"])
async def test_simple_sparql(client, admin_headers, domain):
    qstr = """
select ?s where {
  ?s a brick:Zone_Air_Temperature_Sensor.
}
"""
    admin_headers.update({"Content-Type": "sparql-query"})
    resp = await client.post(
        QUERY_BASE + "/sparql",
        params={"domain": domain.name},
        data=qstr,
        headers=admin_headers,
    )
    print(resp.json())
    assert resp.json()["results"]["bindings"]


@pytest.mark.asyncio
@pytest.mark.depends(on=["tests/test_domain.py"])
async def test_sparql_equip_tree(client, admin_headers, domain):
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
    resp = await client.post(
        QUERY_BASE + "/sparql",
        params={"domain": domain.name},
        data=qstr,
        headers=admin_headers,
    )
    assert len(resp.json()["results"]["bindings"]) > 2


@pytest.mark.asyncio
@pytest.mark.depends(on=["tests/test_domain.py"])
async def test_sparql_location_tree(client, admin_headers, domain):
    qstr = """
select ?parent ?child where {
  ?parent a/rdfs:subClassOf brick:Location.
  ?child brick:isPartOf+ ?parent.
}
"""
    admin_headers.update({"Content-Type": "sparql-query"})
    resp = await client.post(
        QUERY_BASE + "/sparql",
        params={"domain": domain.name},
        data=qstr,
        headers=admin_headers,
    )
    assert len(resp.json()["results"]["bindings"]) > 4
