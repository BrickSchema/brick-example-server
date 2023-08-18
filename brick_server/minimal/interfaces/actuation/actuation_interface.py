from multidict import MultiDict

from brick_server.minimal.exceptions import DoesNotExistError
from brick_server.minimal.interfaces.actuation.bacnet_actuation import BacnetActuation
from brick_server.minimal.interfaces.actuation.base_actuation import BaseActuation
from brick_server.minimal.interfaces.actuation.dummy_actuation import DummyActuation
from brick_server.minimal.utils import parse_graphdb_result


class ActuationInterface:
    def __init__(self):
        self.actuation_dict = {
            "https://brickschema.org/schema/Brick/ref#BACnetReference": BacnetActuation(),
            "dummy": DummyActuation(),
        }

    async def get_external_references(self, domain, entity_id):
        query = f"""
select distinct ?k ?v where {{
    <{entity_id}> ref:hasExternalReference ?o .
    ?o ?k ?v .
}}
        """
        from brick_server.minimal.dbs import graphdb

        res = await graphdb.query(domain.name, query)
        parsed_result = parse_graphdb_result(res)
        multi_dict = MultiDict(zip(parsed_result["k"], parsed_result["v"]))
        return multi_dict

    async def get_actuation_driver(self, external_references) -> BaseActuation:
        types = external_references.getall(
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        )
        for actuation_type in types:
            if actuation_type in self.actuation_dict:
                return self.actuation_dict[actuation_type]
        else:
            raise DoesNotExistError("actuation_driver", ",".join(types))

    async def actuate(self, domain, entity_id, value):
        # TODO: get actuation_name in brick graph with cache
        external_references = await self.get_external_references(domain, entity_id)
        driver = await self.get_actuation_driver(external_references)
        await driver.actuate(entity_id, value, external_references)
