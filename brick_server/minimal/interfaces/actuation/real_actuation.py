import grpc

from brick_server.minimal.interfaces.actuation import (
    actuation_server_pb2,
    actuation_server_pb2_grpc,
)
from brick_server.minimal.interfaces.actuation.base_actuation import BaseActuation


class RealActuation(BaseActuation):
    def __init__(self, *args, **kwargs):
        pass

    def actuate(self, entity_id, value):
        with grpc.insecure_channel("137.110.160.254:50051") as channel:
            stub = actuation_server_pb2_grpc.ActuationServerStub(channel)
            data = actuation_server_pb2.SensorValue(sensor_id=entity_id, value=value)
            res = stub.ActuateSingleSensor(data)
            if not res.result:
                print(res.detail)
            return res.result, res.detail
        # pass
