from copy import deepcopy

from flask_restplus import Namespace, Api, Resource, fields
from flask_restplus import reqparse

from ..data.models import timeseries_data_model

query_api = Namespace('query', description='Query')

response_template = {
    'result': None,
    'status': 1,
}

query_api.models[timeseries_data_model.name] = timeseries_data_model


reqparser = reqparse.RequestParser()
reqparser.add_argument('query',
                       type = str,
                       location='json',
                       )

