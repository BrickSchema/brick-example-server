from urllib.parse import quote_plus
import pdb
import requests

from .common import ENTITY_BASE, authorize_headers
from .data import znt_id


def test_load_ttl():
    with open('examples/data/bldg.ttl', 'rb') as fp:
        headers = authorize_headers({
            'Content-Type': 'text/turtle',
        })
        resp = requests.post(ENTITY_BASE + '/upload', headers=headers, data=fp, allow_redirects=False)
        assert resp.status_code == 200

def test_get_an_entity():
    headers = authorize_headers()
    resp = requests.get(ENTITY_BASE + '/' + quote_plus(znt_id), headers=headers)
    assert resp.status_code == 200
    assert resp.json()['type'].split('#')[-1] == 'Zone_Air_Temperature_Sensor'
    # How to reuse the response schema?

def test_delete_an_entity():
    headers = authorize_headers()
    resp = requests.get(ENTITY_BASE + '/' + quote_plus(znt_id), headers=headers)
    assert resp.status_code == 200
    assert resp.json()['type'].split('#')[-1] == 'Zone_Air_Temperature_Sensor'
    resp = requests.delete(ENTITY_BASE + '/' + quote_plus(znt_id), headers=headers)
    assert resp.status_code == 200
    resp = requests.get(ENTITY_BASE + '/' + quote_plus(znt_id), headers=headers)
    assert resp.status_code == 404


def test_reload_ttl():
    with open('examples/data/bldg.ttl', 'rb') as fp:
        headers = authorize_headers({
            'Content-Type': 'text/turtle',
        })
        resp = requests.post(ENTITY_BASE + '/upload', headers=headers, data=fp, allow_redirects=False)
        assert resp.status_code == 200
