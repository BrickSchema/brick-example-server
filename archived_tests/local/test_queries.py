
from .common import QUERY_BASE, client

def test_simple_sparql(client):
    qstr = """
select ?s where {
  ?s a brick:Zone_Air_Temperature_Sensor.
}
"""
    headers = {
        'Content-Type': 'sparql-query'
    }
    resp = client.post(QUERY_BASE + '/sparql', data=qstr, headers=headers)
    assert resp.json['tuples']

