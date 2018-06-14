import requests
import json
import numpy as np
import arrow
import pdb
import random

from brick_data.timeseries import *
from brick_data.sparql import BrickSparql

brick_db = BrickSparql('http://localhost:8890/sparql',
                       '1.0.3',
                       base_ns='http://jason.com/')

url = 'http://localhost:7889'
api_endpoint = url + '/api/v1'

def gen_random_metadata(num_rooms):
    generated_entities = []
    for room_num in range(0, num_rooms):
        room = 'room_{0}'.format(room_num)
        znt = 'znt_{0}'.format(room_num)
        cc = 'cc_{0}'.format(room_num)
        headers = {
            'Content-Type': 'text/turtle',
        }
        body = {
            'entities': [
                {
                    'type': 'Zone_Temperature_Sensor',
                    'relationships': [
                    ],
                    'name': znt
                },
                {
                    'type': 'Cooling_Command',
                    'relationships': [
                    ],
                    'name': cc
                },
                {
                    'type': 'Room',
                    'relationships': [
                    ],
                    'name': room
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
        generated_entities += entities

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

if __name__ == '__main__':
    entities = gen_random_metadata(2)
    begin_time = arrow.get(2018,4,1).timestamp
    end_time = arrow.get(2018,4,2).timestamp
    znt_id = entities[0]['entity_id']
    data = gen_random_data('Zone_Temperature_Sensor', begin_time, end_time, znt_id)
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

