from urllib.parse import quote_plus

from .common import ENTITY_BASE, client
from .test_data import znt_id


def test_load_ttl(client):
    with open('examples/data/bldg.ttl', 'rb') as fp:
        headers = {
            'Content-Type': 'text/turtle',
        }
        resp = client.post(ENTITY_BASE + '/upload', headers=headers, data=fp)
        assert resp.status_code == 201

def test_get_an_entity(client):
    resp = client.get(ENTITY_BASE + '/' + quote_plus(znt_id))
    assert resp.status_code == 200
    assert resp.json['type'].split('#')[-1] == 'Zone_Air_Temperature_Sensor'
    # How to reuse the response schema?


