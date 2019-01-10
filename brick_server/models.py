import pdb
import numbers

from flask_restplus import Namespace, Api, Resource, fields

"""
class NumberOrString(Number, String):

    def __init__(self, as_string=False, **kwargs):
        Number.__init__(self, False, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if isinstance(value, numbers.Number):
            return Number._serialize(self, value, attr, obj, **kwargs)
        elif isinstance(value, str):
            return String._serialize(self, value, attr, obj, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            Number._deserialize(self, value, attr, data, **kwargs)
        except TypeError:
            String._deserialize(self, value, attr, data, **kwargs)
"""

class NumberOrString(fields.Raw):
    def format(self, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, numbers.Number):
            return value
