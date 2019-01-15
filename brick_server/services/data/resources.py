import pdb

import arrow
from flask import request
from injector import inject
from flask_restplus import Namespace, Api, Resource
from brick_data.timeseries import BrickTimeseries

from .models import reqparser, data_api, timeseries_data_model

@data_api.route('/timeseries/<string:entity_id>', methods=['get', 'delete', 'post'])
class TimeseriesById(Resource):
    @inject
    def __init__(self, db: BrickTimeseries, api):
        super(TimeseriesById, self).__init__(api)
        self.db = db

    @data_api.marshal_with(timeseries_data_model)
    @data_api.response(200, 'Sucess', model=timeseries_data_model)
    @data_api.response(401, 'Server Error')
    @data_api.param('entity_id', 'The ID of an entity for the data request.')
    @data_api.param('start_time', 'Starting time of the data', _in='query')
    @data_api.param('end_time', 'Ending time of the data', _in='query')
    def get(self, entity_id):
        """
        """
        args = reqparser.parse_args()
        start_time = args['start_time']
        end_time = args['end_time']
        res = self.db.query(start_time, end_time, [entity_id])
        data = [[entity_id, arrow.get(row[1]).timestamp, row[2]] for row in res]
        res = {
            'data': data,
            'fields': ['uuid', 'timestamp', 'value']
        }
        return res

    @data_api.param('entity_id', 'The ID of an entity for the data request.')
    @data_api.param('start_time', 'Starting time of the data', _in='query')
    @data_api.param('end_time', 'Ending time of the data', _in='query')
    @data_api.response(200, 'Sucess')
    def delete(self, entity_id):
        args = reqparser.parse_args()
        start_time = args['start_time']
        end_time = args['end_time']
        self.db.delete(start_time, end_time, [entity_id])
        return None

    @data_api.param('data', 'Data', _in='body')
    @data_api.response(201, 'Success')
    def post(self, entity_id):
        args = reqparser.parse_args()
        data = args['data']
        self.db.add_data(data)
        return None, 201


@data_api.route('/timeseries', methods=['post'], strict_slashes=False)
class Timeseries(Resource):
    @inject
    def __init__(self, db: BrickTimeseries, api):
        super(Timeseries, self).__init__(api)
        self.db = db

    @data_api.param('data', 'Data', _in='body')
    @data_api.response(201, 'Success')
    def post(self):
        args = reqparser.parse_args()
        data = args['data']
        self.db.add_data(data)
        return None, 201
