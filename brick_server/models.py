import pdb
import numbers

from flask_restplus import Namespace, Api, Resource, fields


class NumberOrString(fields.Raw):
    def format(self, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, numbers.Number):
            return value
