import pdb

import arrow

from injector import inject
from flask_restplus import Namespace, Api, Resource
from werkzeug import exceptions

from brick_data.timeseries import BrickTimeseries
from brick_data.sparql import BrickSparql

from .models import timeseries_data_model, query_api, reqparser

@query_api.route('/timeseries', methods=['post'], strict_slashes=False)
class TimeseriesQuery(Resource):
    @inject
    def __init__(self, db: BrickTimeseries, api):
        super(TimeseriesQuery, self).__init__(api)
        self.db = db

    @query_api.doc(description='Raw SQL query for timeseries. (May not be exposed in the production deployment.')
    @query_api.expect('query', 'Query', _in='body')
    @query_api.param('query', 'Query', _in='body')
    @query_api.response(200, 'Success', model=timeseries_data_model)
    @query_api.marshal_with(timeseries_data_model)
    def post(self):
        args = reqparser.parse_args()
        qstr = args['query']
        res = self.db.raw_query(qstr)
        data = [[row[0], arrow.get(row[1]).timestamp, row[2]] for row in res]
        res = {
            'data': data,
            'fields': ['uuid', 'timestamp', 'value']
        }
        return res, 200


@query_api.route('/sparql', methods=['post'], strict_slashes=False)
class SparqlQuery(Resource):
    @inject
    def __init__(self, db: BrickSparql, api):
        super(SparqlQuery, self).__init__(api)
        self.db = db

    @query_api.doc(description='Raw SPARQL for Brick metadata. (May not be exposed in the production deployment.')
    @query_api.expect('query', 'Query', _in='body')
    @query_api.param('query', 'Query', _in='body')
    @query_api.response(200, 'Success')
    def post(self):
        args = reqparser.parse_args()
        qstr = args['query']
        raw_res = self.db.query(qstr)
        raise exceptions.NotImplemented('Not implemented yet')
        return res, 200
