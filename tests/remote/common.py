import os
from copy import deepcopy

import pytest

os.environ["BRICK_CONFIGFILE"] = 'configs/configs.json'

#from brick_server.configs import configs

#BRICK_VERSION = configs['brick']['brick_version']
BRICK_VERSION = '1.0.3'

HOSTNAME = 'http://localhost:8000'
#HOSTNAME = 'http://bd-testbed.ucsd.edu:8000'
#HOSTNAME = ''
API_BASE = HOSTNAME + '/brickapi/v1'
ENTITY_BASE = API_BASE + '/entities'
QUERY_BASE = API_BASE + '/queries'
DATA_BASE = API_BASE + '/data'
ACTUATION_BASE = API_BASE + '/actuation'


default_headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2MTM4MTg0MTkuNjI0MDA2NX0.CtZbocAIdfS8zghU6ruCs1WHseTsu9xZeQzSgah8yryJqjRoiOb8vVFsCgtmBJNhFRZKeg2BuImJQgCoVUo0a7GP0A85EeaG6TpjER8wdJRPDC9s3_CqWzUWF3C64Fij2ZDvYpt4cTy8T9NEZ9uOdtOmSUwnI2rZtVBH_l16stzELFQsFa6XeQwMekus-2Yt4LM3nAsaDU5_TfYhoTlDAWjDrKeADE4TmZg9vN_TTipel-0ZXT8fKhifBDYjyAxfpgdlnotg2NNO8ozr1mvLb-Qtx7KX561LSYO0P08k6Frb2JcxXeb3yYkRumte-CffVuaknBOLATYALgDoxMGIgxU71w0LXo99iGFooBi4AM15rssCmBrlBJdS3DUnLDkaWgQeAWEHszAo9hB_rfAhX1xxC4t0yqOBt_blg0gZNiNM7wXqVBQXZA9TjcRXnV8EqQ7EA2dTMkQ7dwqSuuK5NZaY67-B5AKMTyUrHuF0m3FbjsIPQAI_aO9WiLPwqSHGWwD8BsNvvm9pAogy8IUypJA6IepyODOkkLzx5KMeh73Q83fo3wqdmaB-d2XP08p5buvnJmJxZB_LR_ZowJxADtWaIuRgBEb_r5R-nPOizcwIAgdHnyKyogSECZ8dXuaaOmE1b9pfcZmkaN-JWucRTyOFtVfZG82nYjjSWGApqP0',
}


def authorize_headers(headers={}):
    headers.update(default_headers)
    return headers
