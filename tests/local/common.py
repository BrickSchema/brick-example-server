import os

import pytest

os.environ["BRICK_CONFIGFILE"] = 'configs/configs.json'
from brick_server import create_app

from brick_server.configs import configs

#BRICK_VERSION = configs['brick']['brick_version']
BRICK_VERSION = '1.0.3'

HOSTNAME = ''
API_BASE = HOSTNAME + '/brickapi/v1'
ENTITY_BASE = API_BASE + '/entities'
QUERY_BASE = API_BASE + '/queries'
DATA_BASE = API_BASE + '/data'
ACTUATION_BASE = API_BASE + '/actuation'

app = create_app()
app.config['TESTING'] = True

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client
