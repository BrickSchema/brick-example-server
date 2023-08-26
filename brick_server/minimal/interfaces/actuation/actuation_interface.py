from brick_server.minimal.exceptions import DoesNotExistError
from brick_server.minimal.interfaces.actuation.bacnet import BacnetActuation
from brick_server.minimal.interfaces.actuation.base_actuation import BaseActuation
from brick_server.minimal.interfaces.actuation.metasys import MetasysActuation
from brick_server.minimal.utils import get_external_references


class ActuationInterface:
    def __init__(self):
        self.actuation_dict = {
            "https://brickschema.org/schema/Brick/ref#BACnetReference": BacnetActuation(),
            "https://brickschema.org/schema/Brick/ref#MetasysReference": MetasysActuation(),
        }

    async def get_actuation_driver(self, external_references) -> BaseActuation:
        types = external_references.getall(
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        )
        for actuation_type in types:
            if actuation_type in self.actuation_dict:
                return self.actuation_dict[actuation_type]
        raise DoesNotExistError("actuation_driver", ",".join(types))

    async def actuate(self, domain, entity_id, value):
        # TODO: get actuation_name in brick graph with cache
        external_references = await get_external_references(domain, entity_id)
        driver = await self.get_actuation_driver(external_references)
        await driver.actuate(entity_id, value, external_references)
