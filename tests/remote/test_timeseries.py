from urllib.parse import quote_plus
import pdb
import time
import requests

from .common import DATA_BASE
from .data import znt_id, znt_data, znt_t0, znt_t1


def test_post_timeseries():
    body = {
        'data': znt_data,
        'fields': ['uuid', 'timestamp', 'number'],
    }
    resp = requests.post(DATA_BASE + '/timeseries', json=body)
    assert resp.status_code == 200

def test_get_timeseries():
    url = DATA_BASE + '/timeseries/' + quote_plus(znt_id) + '?start_time={0}&?end_time={1}'.format(znt_t0 - 1, znt_t1 + 1)
    resp = requests.get(url)
    assert resp.status_code == 200
    assert resp.json()['data']

def test_delete_timeseries():
    url = DATA_BASE + '/timeseries/' + quote_plus(znt_id)
    params = {
        'start_time': znt_t0 - 1,
        'end_time': znt_t1 + 1,
    }
    resp = requests.delete(url, params=params)
    assert resp.status_code == 200

    resp = requests.get(url, params=params)
    assert not resp.json()['data']
