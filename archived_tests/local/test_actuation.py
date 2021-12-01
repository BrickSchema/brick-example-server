from urllib.parse import quote_plus

from .common import ACTUATION_BASE, client
from .test_data import zntsp_id


def test_actuation_valid(client):
    body = {
        'value': 70,
    }
    resp = client.post(ACTUATION_BASE + '/' + quote_plus(zntsp_id), json=body)
    assert resp.status_code == 200
