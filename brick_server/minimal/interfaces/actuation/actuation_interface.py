from brick_server.minimal.exceptions import DoesNotExistError
from brick_server.minimal.interfaces.actuation.base_actuation import BaseActuation
from brick_server.minimal.interfaces.actuation.dummy_actuation import DummyActuation
from brick_server.minimal.interfaces.actuation.real_actuation import RealActuation


class ActuationInterface:
    def __init__(self):
        self.actuation_dict = {
            "real": RealActuation(),
            "dummy": DummyActuation(),
        }

    def get_actuation_driver(self, entity_id) -> BaseActuation:
        # TODO: get actuation_name in brick graph with cache
        actuation_name = "real"

        if actuation_name in self.actuation_dict:
            return self.actuation_dict[actuation_name]
        else:
            raise DoesNotExistError("actuation_driver", actuation_name)

    async def actuate(self, entity_id, value):
        driver = self.get_actuation_driver(entity_id)
        await driver.actuate(entity_id, value)
