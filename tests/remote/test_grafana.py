from urllib.parse import quote_plus
import json
import time
import requests
from pdb import set_trace as bp

from .common import GRAFANA_BASE, authorize_headers
from .data import *



def test_create_dashbaord():
    headers = authorize_headers()
    url = GRAFANA_BASE + '/'
    resp = requests.post(url, headers=headers)
    assert resp.status_code in [200, 409]

def test_get_dashboard():
    headers = authorize_headers()
    url = GRAFANA_BASE + '/'
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 200

def test_get_dashboard_detail():
    headers = authorize_headers()
    url = GRAFANA_BASE + '/details'
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 200

def test_update_dashboard():
    headers = authorize_headers()
    grafana_model = json.load(open('brick-server-minimal/tests/remote/grafana_body2.json'))

    url = GRAFANA_BASE + '/'
    resp = requests.post(url, headers=headers, json=grafana_model)
    assert resp.status_code == 200

