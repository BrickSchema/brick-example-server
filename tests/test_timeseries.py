import pytest

from tests.common import DATA_BASE, QUERY_BASE
from tests.data import (
    znt_data,
    znt_id,
    znt_t0,
    znt_t1,
    zntsp_data,
    zntsp_id,
    zntsp_t0,
    zntsp_t1,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("data", [znt_data, zntsp_data])
@pytest.mark.depends(on=["tests/test_domain.py"])
async def test_post_timeseries(client, admin_headers, domain, data):
    body = {
        "data": data,
        "fields": ["uuid", "timestamp", "number"],
    }
    resp = await client.post(
        DATA_BASE + "/timeseries",
        params={"domain": domain.name},
        json=body,
        headers=admin_headers,
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "entity_id,t0,t1",
    [
        (znt_id, znt_t0, znt_t1),
        (zntsp_id, zntsp_t0, zntsp_t1),
    ],
)
@pytest.mark.depends(on=["test_post_timeseries"])
async def test_get_timeseries(client, admin_headers, domain, entity_id, t0, t1):
    url = DATA_BASE + "/timeseries"
    params = {
        "domain": domain.name,
        "entity_id": entity_id,
        "start_time": t0 - 1,
        "end_time": t1 + 1,
    }
    resp = await client.get(url, params=params, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]


@pytest.mark.asyncio
@pytest.mark.depends(on=["test_get_timeseries"])
async def test_simple_sql(client, admin_headers, domain):
    qstr = f"""
select * from brick_data_{domain.name} LIMIT 10;
"""
    admin_headers.update({"Content-Type": "application/sql"})
    resp = await client.post(
        QUERY_BASE + "/timeseries", data=qstr, headers=admin_headers
    )
    assert resp.status_code == 200
    assert resp.json()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "entity_id,t0,t1",
    [
        (znt_id, znt_t0, znt_t1),
        (zntsp_id, zntsp_t0, zntsp_t1),
    ],
)
@pytest.mark.depends(on=["test_simple_sql"])
async def test_delete_timeseries(client, admin_headers, domain, entity_id, t0, t1):
    url = DATA_BASE + "/timeseries"
    params = {
        "domain": domain.name,
        "entity_id": entity_id,
        "start_time": t0 - 1,
        "end_time": t1 + 1,
    }
    resp = await client.delete(url, params=params, headers=admin_headers)
    assert resp.status_code == 200

    resp = await client.get(url, params=params, headers=admin_headers)
    assert not resp.json()["data"]
