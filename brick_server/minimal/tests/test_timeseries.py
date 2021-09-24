import pytest

from brick_server.minimal.tests.common import DATA_BASE
from brick_server.minimal.tests.data import (
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
async def test_post_timeseries(client, admin_headers, data):
    body = {
        "data": data,
        "fields": ["uuid", "timestamp", "number"],
    }
    resp = await client.post(
        DATA_BASE + "/timeseries", json=body, headers=admin_headers
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id,t0,t1",
    [
        (znt_id, znt_t0, znt_t1),
        (zntsp_id, zntsp_t0, zntsp_t1),
    ],
)
@pytest.mark.depends(on=["test_post_timeseries"])
async def test_get_timeseries(client, admin_headers, id, t0, t1):
    url = (
        DATA_BASE
        + "/timeseries/"
        + id
        + "?start_time={}&end_time={}".format(t0 - 1, t1 + 1)
    )
    resp = await client.get(url, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id,t0,t1",
    [
        (znt_id, znt_t0, znt_t1),
        (zntsp_id, zntsp_t0, zntsp_t1),
    ],
)
@pytest.mark.depends(on=["test_get_timeseries"])
async def test_delete_timeseries(client, admin_headers, id, t0, t1):
    url = DATA_BASE + "/timeseries/" + id
    params = {
        "start_time": t0 - 1,
        "end_time": t1 + 1,
    }
    resp = await client.delete(url, params=params, headers=admin_headers)
    assert resp.status_code == 200

    resp = await client.get(url, params=params, headers=admin_headers)
    assert not resp.json()["data"]
