import os
from copy import deepcopy

import pytest

BRICK_VERSION = '1.0.3'

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
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2MTQ0ODcxODguNTcyMDI1fQ.VHUnZTaMQuAV8I6jTgVV8e5r0RpTt1fF27DCJqJ_VMIaYrY4DKJ_lwmuDd5CFfiOkvqFDmqBoB0zjwpgqXh5xbCQcMOEDbHDlvETEYnTeIY-c8vkwKwTgtdhHs0rc3JFkvkZb6Y4Q5zmKiABv2qwW1WTGHZbT6KTGpro7JBUQILCQJIpqTVei30xpf0iiXYZplFesMLqSTUSNIxu5CovwxJGsy2cAg6ehk29t-2lU5NSV6a9wMfRDQt2DyR3pd7M2GJLDFO3GFuC7VrBi_2tGh3tm6gjXuUoypC6IhlndxN07YzFDqEC5gdFXVRQ6I1Fpwlk4nQWqGySmVImGwx85_h0wB0nXIa5OdaS4lUjAi8JUqApTr50f4KGqY8Ws3lHSuT3p863rIV6puqc9Zfu0uypIcg0zbgzBzMrOq4OZ_D_BKOzZoxbORWTYdw3tc_LLFw8wF2cBUgSTs1FUm2v0rW7BLGBCnjvtAfoxhJxaOqJOweIY8wwCkHnYUvJvJ6FEQjRSKIsUes-ZJzYHkDabvdsSP6c8Tl24pa_qPz6Sqw4tZpb_WjM0byOV0o-w7DDo9odoTVz34fSdkUCXZvpHyQo3AtmsOBgV-TDhy-27CT7DAqDD7TZM8Pi6ZuU0r1D3ysS7PKUMPL73lo6RvNdsJr9mRoWlCdQ6_fJ2ieVlpU'
}


def authorize_headers(headers={}):
    headers.update(default_headers)
    return headers
