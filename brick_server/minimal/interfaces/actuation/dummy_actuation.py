from brick_server.minimal.interfaces.actuation.base_actuation import BaseActuation


class DummyActuation(BaseActuation):
    def __init__(self, *args, **kwargs):
        pass

    async def actuate(self, entity_id, value):
        return True
