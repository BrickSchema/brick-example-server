import os
from copy import deepcopy

import pytest

BRICK_VERSION = '1.0.3'

HOSTNAME = 'http://bd-testbed.ucsd.edu:8000'
#HOSTNAME = 'https://bd-testbed.ucsd.edu'
#HOSTNAME = 'http://bd-testbed.ucsd.edu:8000'
#HOSTNAME = ''
API_BASE = HOSTNAME + '/brickapi/v1'
ENTITY_BASE = API_BASE + '/entities'
QUERY_BASE = API_BASE + '/rawqueries'
DATA_BASE = API_BASE + '/data'
ACTUATION_BASE = API_BASE + '/actuation'


default_headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2MTQ0NzAwNDQuNzkzNDE2N30.EUL7qwVnqLflcc-_CP4ge-VooAzgiAwihYqzzSV4PJ1xZN1aOczxNPevySi-e6EGTlo5LYQwYfBZXUF45XzA6fCYLRhJ-ofx_kkXvxcXVdEvyR1ZEZJepCoLo345IH1xCiHkFbZ2e4gnpKZVAMy1LB1OKREqUmIu4HOzX6RixRHxqTbE9SYMGdaMNumf7xLoc_PgnUMj7Tf3ciAPKdL8oOb-0y0au7pH6fiqflCcetM1gHlZfkJgOdINhSPWNECtX7BcJ4n10uQlDO4d5EEoY_6ggB0LOMDthewGnW7W7UaCdD4y76KhRw6MS7jb7teyUVXAO8GYFeZWkkH_8sSwnOZNNlsrXo3uusbj0xxO0JEHjbg3k3gD86Y825qMChDAQf3aOfpsyCvnfF5WG6alwOieCpbfkoyB6GS6t7FSLCcGcmYEa2poWbqRmlC7e1vW5WYAZsNnfs_vZcTktGVjvQ36Bf292azt34r2Svhyufe9hICQiiY7t9zSMMchwbO5qLIy0TGayivKbjlylcV2ZIiPDuTmjd3Fgb-zPsxWap8ecI7CoQ4fbahO8R1AlcfEq1z8tYK0UGFj5sBiT3gTDuPabnEQcoG9iqQGqB1LwBGAKwKE8xpZGQAOpcjf47MwxumyIAaQdyhdVgjHwRJXFZwzTHRKWd2cJtZWRfGTurs',
}


def authorize_headers(headers={}):
    headers.update(default_headers)
    return headers
