from urllib.parse import quote_plus

from .common import DATA_BASE, client
from .test_data import znt_id, znt_data, znt_t0, znt_t1


def test_post_timeseries(client):
    body = {
        'data': znt_data,
        'fields': ['uuid', 'timestamp', 'number'],
    }
    resp = client.post(DATA_BASE + '/timeseries', json=body)
    assert resp.status_code == 201

def test_get_timeseries(client):
    url = DATA_BASE + '/timeseries/' + znt_id + '?start_time={0}&?end_time={1}'.format(znt_t0 - 1, znt_t1 + 1)
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.json['data']
