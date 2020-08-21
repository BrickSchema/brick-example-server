from urllib.parse import quote_plus
import time
import requests
from pdb import set_trace as bp

from .common import GRAFANA_BASE, authorize_headers
from .data import *



def test_create_dashbaord():
    headers = authorize_headers()
    url = GRAFANA_BASE + '/'
    resp = requests.post(url, headers=headers)
    assert resp.status_code in [201, 409]

def test_get_dashboard():
    headers = authorize_headers()
    url = GRAFANA_BASE + '/'
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 200

