from flask_restplus import Namespace, fields, Model
from flask_restplus import reqparse

from ...models import NumberOrString

entity_api = Namespace('entities', description='Entity')

response_template = {
    'result': None,
    'status': 1,
}

entity_model = Model('Entity', {
    'type': fields.String,
    'relationships': fields.List(fields.List(fields.String))
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
