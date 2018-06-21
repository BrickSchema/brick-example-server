import requests
import json
import numpy as np
import arrow
import random
import pdb

from brick_data.timeseries import *
from brick_data.sparql import BrickSparql

url = 'http://localhost:7889'
api_endpoint = url + '/api/v1'

def post_random_metadata(num_rooms):
    generated_entities = {}
    for room_num in range(0, num_rooms):
        room_name = 'room_{0}'.format(room_num)
        znt_name = 'znt_{0}'.format(room_num)
        cc_name = 'cc_{0}'.format(room_num)
        headers = {
            'Content-Type': 'text/turtle',
        }
        body = {
            'entities': [
                {
                    'type': 'Zone_Temperature_Sensor',
                    'relationships': [
                    ],
                    'name': znt_name
                },
                {
                    'type': 'Cooling_Command',
                    'relationships': [
                    ],
                    'name': cc_name
                },
                {
                    'type': 'Room',
                    'relationships': [
                    ],
                    'name': room_name
                }
            ],
        }


        #resp = requests.post(api_endpoint + '/entities', data=q, headers=headers, )
        resp = requests.post(api_endpoint + '/entities', json=body)
        assert resp.status_code == 201
        entities = resp.json()['entities']
        znt_id = entities[0]['entity_id']
        cc_id = entities[1]['entity_id']
        room_id = entities[2]['entity_id']
        body = {
            'relationships': [['bf:hasLocation', room_id]],
        }
        generated_entities[znt_name] = znt_id
        generated_entities[cc_name] = cc_id
        generated_entities[room_name] = room_id

        resp = requests.post(api_endpoint + '/entities/{0}'.format(znt_id), json=body)
        assert resp.status_code == 201
        resp = requests.post(api_endpoint + '/entities/{0}'.format(cc_id), json=body)
        assert resp.status_code == 201
    return generated_entities

def gen_random_data(point_type, begin_time, end_time, srcid):
    latency_base = 300 # seconds
    latency_noise_factor = 30 # seconds
    if point_type == 'Zone_Temperature_Sensor':
        max_val = 80
        min_val = 60
        day_interval = 24 * 60 * 60
        noise_size = max_val * 0.01 # ratio
        noiser = np.vectorize(
            lambda x: x + random.random() * noise_size - noise_size / 2)
        data = []
        # Add data with linear interpolation + noise
        t = begin_time
        xs = []
        ys = None
        while t < end_time:
            next_t = t + day_interval
            xp = [t, t + day_interval / 2, next_t]
            yp = [min_val, max_val, min_val]
            x = [point + random.random() * latency_noise_factor
                 - latency_noise_factor / 2
                 for point in range(t, next_t, latency_base)]
            y = noiser(np.interp(x, xp, yp))
            xs += x
            if not ys:
                ys = y
            else:
                ys = np.concatenate([ys, y])
            t = next_t
    data = [[srcid, x, y] for x, y in zip(xs, ys)]
    return data

def post_random_data(data):
    url = api_endpoint + '/data/timeseries'.format(znt_id)
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'data': data,
        'fields': ['uuid', 'timestamp', 'value'],
    }
    resp = requests.post(url, json=payload, headers=headers)
    assert resp.status_code == 201

def get_timeseries_data(entity_id, begin_time, end_time):
    url = api_endpoint + '/data/timeseries/{0}'.format(znt_id)
    params = {
        'begin_time': begin_time,
        'end_time': end_time,
    }
    resp = requests.get(url, params=params)
    data = resp.json()['data']
    return data

def delete_timeseries_data(entity_id, begin_time, end_time):
    url = api_endpoint + '/data/timeseries/{0}'.format(znt_id)
    params = {
        'begin_time': begin_time,
        'end_time': end_time,
    }
    resp = requests.delete(url, params=params)
    assert resp.status_code == 200

def get_entity_by_id(entity_id):
    url = api_endpoint + '/entities/{0}'.format(entity_id)
    resp = requests.get(url)
    if resp.status_code == 404:
        print(entity_id, 'non found')
        return None
    else:
        return resp.json()

def delete_entity_by_id(entity_id):
    #TODO: Implement this inside the server
    url = api_endpointa + 'entities/{0}'.format(entity_id)
    resp = requests.delete(url)
    assert resp.status_code == 200

def query_sparql(query):
    url = api_endpoint + '/queries/sparql'
    headers = {
        'Content-Type': 'sparql-query',
    }
    resp = requests.post(url, data=query)
    return resp.json()

if __name__ == '__main__':
    # Entities testing
    entity_ids = post_random_metadata(2)
    begin_time = arrow.get(2018,4,1).timestamp
    end_time = arrow.get(2018,4,2).timestamp
    znt_id = entity_ids['znt_0']
    znt_entity = get_entity_by_id(znt_id)
    assert znt_entity
    not_existing_entity = get_entity_by_id('some_non_eixsting_id')
    assert not not_existing_entity
    print('Metadata Test Success')

    # Timeseries testing
    data = gen_random_data('Zone_Temperature_Sensor', begin_time, end_time, znt_id)
    post_random_data(data)
    received_data = get_timeseries_data(znt_id, begin_time, end_time)
    assert received_data
    delete_timeseries_data(znt_id, begin_time, end_time)
    received_data = get_timeseries_data(znt_id, begin_time, end_time)
    assert received_data == []
    print('Timeseries Data Test Success')

    # Raw SPARQL testing
    query = """
    select ?point where {{
    ?point bf:hasLocation :{0}.
    }}
    """.format(entity_ids['room_0'])
    res = query_sparql(query)
    assert res['tuples']
    print('Raw QPARQL Test Success')



