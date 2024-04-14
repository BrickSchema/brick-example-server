import time

from brick_server.minimal.interfaces.actuation.bacnet import BacnetActuation
from brick_server.minimal.interfaces.actuation.base_actuation import BaseActuation
from brick_server.minimal.interfaces.actuation.metasys import MetasysActuation
from brick_server.minimal.interfaces.cache import use_cache
from brick_server.minimal.utilities.exceptions import BizError, ErrorCode
from brick_server.minimal.utilities.utils import get_external_references


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
        raise BizError(ErrorCode.ActuationDriverNotFoundError, ",".join(types))

    async def actuate(self, domain, entity_id, value):
        # TODO: get actuation_name in brick graph with cache
        start = time.time()
        driver_time = 0
        actuation_time = 0
        try:
            cache_key = f"external_references:{domain.name}:{entity_id}"
            external_references = await use_cache(
                cache_key, get_external_references, domain, entity_id
            )
            driver = await self.get_actuation_driver(external_references)
            driver_time = time.time() - start
            start = time.time()
            success, detail = await driver.actuate(
                entity_id, value, external_references
            )
            actuation_time = time.time() - start
        except Exception as e:
            success, detail = False, f"{e}"
        return success, detail, driver_time, actuation_time
