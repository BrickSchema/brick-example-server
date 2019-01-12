from flask import Blueprint
from flask_restplus import Api

blueprint = Blueprint('api', __name__)
api = Api(blueprint, title='API', description='API')

from .services.data.resources import data_api
api.add_namespace(data_api)
from .services.queries.resources import query_api
api.add_namespace(query_api)
from .services.entities.resources import entity_api
api.add_namespace(entity_api)
