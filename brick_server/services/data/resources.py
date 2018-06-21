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

    @data_api.doc(description='Get data of an entity with in a time range.')
    @data_api.marshal_with(timeseries_data_model)
    @data_api.response(200, 'Data loaded', model=timeseries_data_model)
    @data_api.param('entity_id', 'The ID of an entity for the data request.', _in='url')
    @data_api.param('start_time', 'Starting time of the data in UNIX timestamp in seconds (float)', _in='query')
    @data_api.param('end_time', 'Ending time of the data UNIX timestamp in seconds (float)', _in='query')
    def get(self, entity_id):
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

    @data_api.doc(description='Delete data of an entity with in a time range or all the data if a time range is not given.')
    @data_api.param('entity_id', 'The ID of an entity for the data request.', _in='url')
    @data_api.param('start_time', 'Starting time of the data in UNIX timestamp in seconds (float)', _in='query')
    @data_api.param('end_time', 'Ending time of the data UNIX timestamp in seconds (float)', _in='query')
    @data_api.response(200, 'Sucess')
    def delete(self, entity_id):
        args = reqparser.parse_args()
        start_time = args['start_time']
        end_time = args['end_time']
        self.db.delete(start_time, end_time, [entity_id])
        return None, 200


@data_api.route('/timeseries', methods=['post'], strict_slashes=False)
class Timeseries(Resource):
    @inject
    def __init__(self, db: BrickTimeseries, api):
        super(Timeseries, self).__init__(api)
        self.db = db

    @data_api.doc(description='Post data. If fields are not given, default values are assumed.')
    @data_api.response(201, 'Success')
    @data_api.expect(timeseries_data_model, validate=False) # TODO: Enable this line.
    def post(self):
        args = reqparser.parse_args()
        raw_data = args['data']
        fields = args.get('fields')
        if fields:
            uuid_idx = fields.index('uuid')
            timestamp_idx = fields.index('timestamp')
            value_idx = fields.index('value')
            data = [[datum['uuid'], datum['timestamp'], datum['value']]
                    for datum in raw_data]
        else:
            data = raw_data
        self.db.add_data(data)
        return None, 201
