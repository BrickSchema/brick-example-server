from flask_restplus import Namespace, fields, Model
from flask_restplus import reqparse

from ...models import NumberOrString

entity_api = Namespace('entities', description='Manage entities')
entity_model = Model('Entity', {
    'type': fields.String(example='Zone_Temperature_Sensor'),
    'relationships': fields.List(fields.List(fields.String),
                                 example=[['bf:hasLocation', 'room_1']])
})
entity_api.models[entity_model.name] = entity_model

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
