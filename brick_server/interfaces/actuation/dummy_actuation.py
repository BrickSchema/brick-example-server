

from .base_actuation import BaseActuation


class DummyActuation(BaseActuation):
    def __init__(self, *args, **kwargs):
        pass

    def actuate(self, entity_id, value):
        return True
