import os
from copy import deepcopy

import pytest

BRICK_VERSION = '1.0.3'

HOSTNAME = 'https://bd-testbed.ucsd.edu:8080'
#HOSTNAME = 'https://bd-testbed.ucsd.edu'
#HOSTNAME = 'http://bd-testbed.ucsd.edu:8000'
#HOSTNAME = ''
API_BASE = HOSTNAME + '/brickapi/v1'
ENTITY_BASE = API_BASE + '/entities'
QUERY_BASE = API_BASE + '/rawqueries'
DATA_BASE = API_BASE + '/data'
ACTUATION_BASE = API_BASE + '/actuation'


default_headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2MTQzOTUzNDcuOTkxMDg4fQ.MsTv8UHjpPLKd2DdP1-b1nJzQWC4m4r7I3T4q0wJRG2UxLxUwhCKjUx0TYsDYOQQIZo6M8UPiKXz_Hnqd6tOq7ZSsi1cSng4VcB4Mbr9MpL8C19MN7imEIR_0aGB1iebEMKTK1Qdt4sRoLl_Z1bYTQtg97qKs-teZxhFUDEvxpRISUgeVC3Vbe24EujF4HbGiJZGkuZqHwLO76TqtWIqBUQnNQVJ8hrc6QYyZaFMe1FX7EkmSTkPjh770cEHFiVfxyoANSSYoC6REtE0UIuL9hBJzKGxuy6uUFKJZTXl8AIFJ-YHj0pB4t3IANqw2WNrSfrSHAy--U9Hl_dA1h9lZTqurnr6xOi37KnS1xTBHRbTnBuaENsw6wtLO-VmBtwV2yFz69TibNAQPD3O7Ns8LbURTnocuVeJoXujk_4bi1aRodZcKSyhS_xhsx4KhEmRyziHnKEjXpouVtkLFsyYQgnpQTixEHkxdsuaW4jR_A1P8v4lY1Vjm45OafSqqTdAB3-V3sQUSxeExKVtEMctU-MbDM71b2kuMP3hu_eEuULYC1Jour1vK-aLtND9JyGlS-eVndyOoEUKxPtYbTa0RfVuhYtqq_6UWQKmOf_DkoH5lInNIu7WQxpvF9KHQp1rEoxfwaS6PAeYc3gO_kvN3tWp0icxmGdx7vZAQEPIfKU',
}


def authorize_headers(headers={}):
    headers.update(default_headers)
    return headers
