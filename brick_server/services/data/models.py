from flask_restplus import Namespace, fields, Model
from flask_restplus import reqparse

from ...models import NumberOrString

data_api = Namespace('data', description='Data')
timeseries_data_model = Model(
    'TimeseriesData', {
        'data': fields.List(fields.List(NumberOrString()),
                            example= [['uuid-abcd', 1547526087, 70.0],
                                      ['uuid-abcd', 1547526187, 71.0]]
                            ),
        'fields': fields.List(fields.String(enum=['uuid', 'timestamp', 'value']),
                              default=['uuid', 'timestamp', 'value']),
    }
)
data_api.models[timeseries_data_model.name] = timeseries_data_model

reqparser = reqparse.RequestParser()
reqparser.add_argument('start_time',
                       type=float,
                       location='args',
                       default=None,
                       )
reqparser.add_argument('end_time',
                       type=float,
                       location='args',
                       default=None,
                       )
reqparser.add_argument('data',
                       type = list,
                       location='json',
                       )
reqparser.add_argument('query',
                       type = str,
                       location='json',
                       )

