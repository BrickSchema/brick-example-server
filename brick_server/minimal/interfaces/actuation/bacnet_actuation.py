import grpc
from loguru import logger

from brick_server.minimal.interfaces.actuation import (
    actuation_server_pb2,
    actuation_server_pb2_grpc,
)
from brick_server.minimal.interfaces.actuation.base_actuation import BaseActuation


class BacnetActuation(BaseActuation):
    def __init__(self, *args, **kwargs):
        pass

    async def actuate(self, entity_id, value, external_references):
        sensor_id = external_references[
            "http://data.ashrae.org/bacnet/2020#object-identifier"
        ]
        logger.info("bacnet: {} {}", sensor_id, value)
        async with grpc.aio.insecure_channel("137.110.160.254:50051") as channel:
            stub = actuation_server_pb2_grpc.ActuationServerStub(channel)
            data = actuation_server_pb2.SensorValue(sensor_id=sensor_id, value=value)
            res = await stub.ActuateSingleSensor(data)
            if not res.result:
                print(res.detail)
            return res.result, res.detail
