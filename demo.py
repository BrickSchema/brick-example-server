#!/usr/bin/env python
import httpx

HOST = "http://bd-datas3.ucsd.edu:9000/brickapi/v1"
admin_jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjIwMTI5MDk4ODguNTc3NzgwMiwiYXBwX2lkIjpudWxsfQ.FgCEkbcv4FfHRv6oe9Y-aPi0z9mvs2VsTaz9nhIFzl8"
headers = {"Authorization": "Bearer " + admin_jwt}

ROOM = "2150"
MAXCFM = 1200

if __name__ == "__main__":
    # sparql query to find the target hvac supply flow setpoint
    qstr = (
        'select ?s where { '
        f'ebu3b:EBU3B_HVAC_Zone_Rm_{ROOM} rdf:type brick:HVAC_Zone .'
        f'?vav brick:feeds ebu3b:EBU3B_HVAC_Zone_Rm_{ROOM} .'
        '?vav rdf:type brick:VAV .'
        '?vav brick:hasPoint ?s .'
        '?s rdf:type brick:Discharge_Air_Flow_Setpoint .'
        '} limit 100' 
    )
    # example to find the airflow setpoints of all vavs on the 2nd floor
    qstr2 = '''
        select ?s where {
            ?zone a brick:HVAC_Zone .
            ?zone brick:isPartOf ebu3b:EBU3B_Floor_2.
            ?vav brick:feeds ?zone .
            ?vav rdf:type brick:VAV .
            ?vav brick:hasPoint ?s .
            ?s rdf:type brick:Discharge_Air_Flow_Setpoint .
        } limit 100
    '''
    # example to find the fan
    qstr3 = '''
    PREFIX brick: <https://brickschema.org/schema/Brick#>
        select ?id where { 
            ?plug a brick:PlugStrip .
            ?plug brick:hasLocation ebu3b:EBU3B_Rm_4262 .
            ?filter a brick:Filter .
            ?plug brick:feeds ?filter .
            ?s brick:isPointOf ?plug.
            ?s a brick:On_Off_Command .
            ?s brick:hasTimeseriesId ?id .
        } limit 100 
    '''
    headers.update({"Content-Type": "sparql-query"})
    resp = httpx.post(HOST+"/rawqueries/sparql", data=qstr3, headers=headers)
    assert len(resp.json()["results"]["bindings"]) == 1
    s = resp.json()["results"]["bindings"][0]['id']['value']
    print(s)
    
    # send command to actuate
    # translation from brick entity_id to object identifier is not yet implemented
    # using hardcoded object id now
    headers.update({'Content-Type': 'application/json'})
    body = {
        s: ['active'] # entity_id: [value, placeholder(optional)], null means revert,
    }
    resp = httpx.post(HOST+'/actuation/', json=body, headers=headers)
    assert resp.status_code == 200
