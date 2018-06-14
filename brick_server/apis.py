from flask import Blueprint
from flask_restplus import Api

blueprint = Blueprint('api', __name__)
api_desc = """
- Questions to https://groups.google.com/forum/#!forum/brickschema
- Official Website: https://brickschema.org
"""
api = Api(blueprint,
          title = 'Brick API Documentation',
          description = api_desc,
          doc = '/doc')

from .services.data.resources import data_api
api.add_namespace(data_api)
from .services.queries.resources import query_api
api.add_namespace(query_api)
from .services.entities.resources import entity_api
api.add_namespace(entity_api)
from .services.actuation.resources import actuate_api
api.add_namespace(actuate_api)
