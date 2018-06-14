from flask_restplus import Namespace, fields, Model
from flask_restplus import reqparse

from ...models import NumberOrString

entity_api = Namespace('entities', description='Manage entities')

relationships_field = {
    'relationships': fields.List(fields.List(fields.String),
                                 example=[['bf:hasLocation', 'room_1']]),
}
relationships_model = Model('Relationships', relationships_field)
"""
entity_field = {
    'type': fields.String(example='Zone_Temperature_Sensor'),
    'relationships': fields.List(fields.List(fields.String),
                                 example=[['bf:hasLocation', 'room_1']]),
    'name': fields.String(example='ZNT101'),
    'entity_id': fields.String(example='b0d8a253-0c6d-4491-b2be-faa965cd72ec'),
}
"""
#entity_model = Model('Entity', entity_field)
entity_model = relationships_model.inherit('Entity', {
    'type': fields.String(example='Zone_Temperature_Sensor'),
    'name': fields.String(example='ZNT101'),
    'entity_id': fields.String(example='b0d8a253-0c6d-4491-b2be-faa965cd72ec'),
})
entities_model = Model('Entities', {
    'entities': fields.List(fields.Nested(entity_model))
})
entity_api.models[relationships_model.name] = relationships_model
entity_api.models[entity_model.name] = entity_model
entity_api.models[entities_model.name] = entities_model

reqparser = reqparse.RequestParser()

reqparser.add_argument('Content-Type',
                       type=str,
                       location='headers',
                       default='application/json',
                       dest='content_type',
                       )
reqparser.add_argument('entities',
                       type = list,
                       location='json',
                       )
reqparser.add_argument('relationships',
                       type = list,
                       location='json',
                       default=[],
                       )
reqparser.add_argument('turtle',
                       type=str,
                       location='form',
                       )
