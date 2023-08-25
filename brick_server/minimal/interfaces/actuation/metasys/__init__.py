import grpc
from loguru import logger

from brick_server.minimal.interfaces.actuation.base_actuation import BaseActuation
from brick_server.minimal.interfaces.actuation.metasys import (
    actuate_pb2,
    actuate_pb2_grpc,
)


class MetasysActuation(BaseActuation):
    def __init__(self, *args, **kwargs):
        pass

    async def actuate(self, entity_id, value, external_references):
        sensor_id = external_references[
            "https://brickschema.org/schema/Brick/ref#metasysID"
        ]
        logger.info("metasys: {} {}", sensor_id, value)
        async with grpc.aio.insecure_channel("localhost:50051") as channel:
            stub = actuate_pb2_grpc.ActuateStub(channel)
            response: actuate_pb2.Response = await stub.TemporaryOverride(
                actuate_pb2.TemporaryOverrideAction(
                    uuid=sensor_id, value=str(value), hour=4, minute=0
                )
            )
            return response.status, response.details