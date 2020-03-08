import os
from copy import deepcopy
from rdflib import Namespace

import pytest

BRICK_VERSION = '1.0.3'
BRICK = Namespace(f'https://brickschema.org/schema/{BRICK_VERSION}/Brick#')

HOSTNAME = 'https://bd-testbed.ucsd.edu:8000'
#HOSTNAME = 'https://bd-testbed.ucsd.edu'
#HOSTNAME = 'http://bd-testbed.ucsd.edu:8000'
#HOSTNAME = ''
API_BASE = HOSTNAME + '/brickapi/v1'
ENTITY_BASE = API_BASE + '/entities'
QUERY_BASE = API_BASE + '/rawqueries'
DATA_BASE = API_BASE + '/data'
ACTUATION_BASE = API_BASE + '/actuation'


default_headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2MTQ4MjYzOTUuODYzNDY3fQ.iAUJCKi7ZznHVpCbls1lHP2owbJfmu4XKGFKE8TVNRGDC3DdiZQHuAkNvB5-3OhmaQVwSbDvQn3moAS3PSCjx7nafetmP2UuNKdji_gIiAA5M66XOPz_nP36vUDc5GKeCYQAmtRMa2vmOlOTOHHBthTW6zBrezchvSl2i5ZC6GJ2MXCv3xh4vFYwjTrinzOGRunfnV6vTsqlN35-g0DE6Wf4dhlQ5vWEimnx2O2CIH0uvzix2hu78pmblgjacb_C7SSKqqgoKss7_HsUomD7r0vY9TAOLEMi50B-spWgTtdtXMlkXsLyDj6mG2NrUy3VMePLvlGlWDDk6UYCHAghRKxv2sCS_n_ELkXZ_Z10ckcEGNWb-MnfDUW0me3Z7FbCtMgirknGkgZt9BCx5pjQ47dqZOwk1p535ZC-WK6T_BkwL_QO1kNfzQbPTI5R13gcp0Ud9fH6MrcFxf3_WbGiI6BJRRC2SLSpyulVEGvJTdRcBRAZeM_M2YPngDtHTb4ZjUNKSMZgAhUQyI9xbJf-8jR5P3JNasK04IJWULjDEHOsY3iAAcRqSqw51-GuoIszdSsdO1QN3BvDvWRPMnAqS2V9fr0i92-A1O5_08DS4GwXoG4DpmWjh6Fx2fzPZQQLFbDCbyIob-mNSFl09smR1epx_dZg8dwHqmJhedJvis4"
}


def authorize_headers(headers={}):
    headers.update(default_headers)
    return headers
