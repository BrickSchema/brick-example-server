from urllib.parse import quote_plus
import time
import requests

from .common import ACTUATION_BASE, authorize_headers
from .data import *



def test_actuation():
    headers = authorize_headers()
    url = ACTUATION_BASE + '/' + quote_plus(zntsp_id)
    body = {
        'value': 60,
    }
    resp = requests.post(url, json=body, headers=headers)
    assert resp.status_code == 200
