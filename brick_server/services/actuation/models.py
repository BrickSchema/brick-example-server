from flask_restplus import Namespace, fields, Model
from flask_restplus import reqparse

from ...models import NumberOrString

actuate_api = Namespace('actuation', description='Actuate entities')
actuation_model = Model('', {
    'type': fields.String(example='Zone_Temperature_Sensor'),
    'relationships': fields.List(fields.List(fields.String),
                                 example=[['bf:hasLocation', 'room_1']])
})
actuate_api.models[actuation_model.name] = actuation_model

reqparser = reqparse.RequestParser()

# For actuation
reqparser.add_argument('relinquish',
                       type = bool,
                       location='json',
                       default=False,
                       )
reqparser.add_argument('value',
                       type = float,
                       location='json',
                       default=None,
                       )
reqparser.add_argument('scheduled_time',
                       type = float,
                       location='json',
                       )
