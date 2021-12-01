from urllib.parse import quote_plus
import requests

from .common import ACTUATION_BASE
from .test_data import zntsp_id


def test_actuation_valid():
    body = {
        'value': 70,
    }
    resp = requests.post(ACTUATION_BASE + '/' + quote_plus(zntsp_id), json=body)
    assert resp.status_code == 200
