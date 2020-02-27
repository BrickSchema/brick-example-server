import os
from copy import deepcopy

import pytest

BRICK_VERSION = '1.0.3'

HOSTNAME = 'http://bd-testbed.ucsd.edu'
#HOSTNAME = 'https://bd-testbed.ucsd.edu'
#HOSTNAME = 'http://bd-testbed.ucsd.edu:8000'
#HOSTNAME = ''
API_BASE = HOSTNAME + '/brickapi/v1'
ENTITY_BASE = API_BASE + '/entities'
QUERY_BASE = API_BASE + '/rawqueries'
DATA_BASE = API_BASE + '/data'
ACTUATION_BASE = API_BASE + '/actuation'


default_headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2MTM4Njg4MTUuMjI3NDQzNX0.nVkZ0tPHmpWnd9hf72wXTcIKRW97e7MrTCyNxqg3ZQy2ZRlzVxgL4YJ-9jnJNPpL8ZO37p-2LtS9_YrglUU9-uxlangUC6uDQvgTGpC8ai__yf4DBByYfxQpCZOsZu0sNQ-PPCPNp6T0bRUjbb-o6dD9YcsSASTA-VqMB8Qz00LLAHJ-nPyTFDjZr59_d92rNOpjk3zbrbRVxD9pjzeEMgrWzKVZMKk10QxYc7w_KF4FUtT0E9AEqlbDhGWyX2OR2rk8IC1Rxd6ZVTh4f60osomb31OBlM6L3puoCP-VP6S_7OW-WqetZw7JQDyALVab4bjo_IUmzqFGhxWnCEYrGz4L9ewtGxemsqWrp6JwW_K8JsVFwMAPHDo07ow2J28mPLc9WWXggFWTJweYQiG-cFuH_LVGoEVR1ajbKJ2an27cQ-zYrSHj5SxI-OZUHcnOSJ-r85EoVBI4H89g9qOKB8Z1MWkwVD9p0rtc_V3Uq7BkPna03KS3MJaNIxttQZdTtD1DOLiOs6vMl_VOoebSDxeS1W-epiSgl2l-Vp89T3vot7tRAnDQgn4RqL1DtZAzeAIjD0C3KhpvS58duYxxyRAnD0fxRF3k3EGAA6QuuCHZdx1bLDvaZkdEM5JBKUVzTo2-GTKXhHzgzeYqY9tw8PLcHyr5yrSasRU4cKjgIkM',
}


def authorize_headers(headers={}):
    headers.update(default_headers)
    return headers
