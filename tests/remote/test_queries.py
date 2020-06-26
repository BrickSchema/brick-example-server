import requests
from pdb import set_trace as bp

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


def test_simple_sql():
    qstr = """
select * from brick_data;
"""
    headers = authorize_headers({
        'Content-Type': 'application/sql'
    })
    resp = requests.post(QUERY_BASE + '/timeseries', data=qstr, headers=headers)
    assert resp.status_code == 200
    assert resp.json()


def test_sparql_equip_tree():
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
    headers = authorize_headers({
        'Content-Type': 'sparql-query'
    })
    resp = requests.post(QUERY_BASE + '/sparql', data=qstr, headers=headers)
    assert len(resp.json()['results']['bindings']) > 2

def test_sparql_location_tree():
    qstr = """
select ?parent ?child where {
  ?parent a/rdfs:subClassOf brick:Location.
  ?child brick:isPartOf+ ?parent.
}
"""
    headers = authorize_headers({
        'Content-Type': 'sparql-query'
    })
    resp = requests.post(QUERY_BASE + '/sparql', data=qstr, headers=headers)
    assert len(resp.json()['results']['bindings']) > 4
