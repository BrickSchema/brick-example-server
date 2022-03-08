from pathlib import Path

from rdflib import Namespace

BRICK_VERSION = "1.1"
BRICK = Namespace(f"https://brickschema.org/schema/{BRICK_VERSION}/Brick#")

API_BASE = "/brickapi/v1"
ENTITY_BASE = API_BASE + "/entities"
QUERY_BASE = API_BASE + "/rawqueries"
DATA_BASE = API_BASE + "/data"
ACTUATION_BASE = API_BASE + "/actuation"
GRAFANA_BASE = API_BASE + "/grafana"
AUTH_BASE = "/auth"

PROJECT_FOLDER = Path(__file__).parent.parent.absolute()
EXAMPLES_DATA_FOLDER = PROJECT_FOLDER / "examples" / "data"
assert EXAMPLES_DATA_FOLDER.is_dir()


# default_headers = {
#     "Authorization": "Bearer " + os.environ['JWT_TOKEN']
# }
#
#
# def authorize_headers(headers={}):
#     headers.update(default_headers)
#     return headers
