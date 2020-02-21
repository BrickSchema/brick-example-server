import requests
import pdb

from .common import QUERY_BASE, ENTITY_BASE, authorize_headers


def test_load_ttl():
    with open('examples/data/bldg.ttl', 'rb') as fp:
        headers = authorize_headers({
            'Content-Type': 'text/turtle',
            #'Media-Type': 'text/plain',
        })
        resp = requests.post(ENTITY_BASE + '/upload', headers=headers, data=fp, allow_redirects=False)
        assert resp.status_code == 200

def test_simple_sparql():
    qstr = """
select ?s where {
  ?s a brick:Zone_Air_Temperature_Sensor.
}
"""
    headers = authorize_headers({
        'Content-Type': 'sparql-query'
    })
    resp = requests.post(QUERY_BASE + '/sparql', data=qstr, headers=headers)
    assert resp.json()['results']['bindings']

