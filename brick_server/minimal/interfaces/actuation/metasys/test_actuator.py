import actuate_pb2
import actuate_pb2_grpc
import grpc

# with grpc.insecure_channel('localhost:50051') as channel:
#     stub = actuate_pb2_grpc.ActuateStub(channel)
#     response: actuate_pb2.Response = stub.TemporaryOverride(actuate_pb2.TemporaryOverrideAction(uuid='4d3ca6b4-562d-52cc-856b-1b3830e59005', value='binarypvEnumSet.bacbinInactive', hour=0, minute=2))
#     print(response.status, response.details)


if __name__ == "__main__":
    target = "02068f28-d239-5f24-9119-c36ef852c0fe"  # cooling output
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = actuate_pb2_grpc.ActuateStub(channel)

        # response: actuate_pb2.Response = stub.TemporaryOverride(actuate_pb2.TemporaryOverrideAction(uuid=target, value='0', hour=4, minute=0))
        # print(response.status, response.details)

        # time.sleep(10*60)
        # response: actuate_pb2.Response = stub.TemporaryOverride(actuate_pb2.TemporaryOverrideAction(uuid=target, value='40', hour=4, minute=0))
        # print(response.status, response.details)

        # time.sleep(20*60)
        # response: actuate_pb2.Response = stub.TemporaryOverride(actuate_pb2.TemporaryOverrideAction(uuid=target, value='25', hour=4, minute=0))
        # print(response.status, response.details)

        # time.sleep(30*60)
        response: actuate_pb2.Response = stub.TemporaryOverride(
            actuate_pb2.TemporaryOverrideAction(
                uuid=target, value="75", hour=4, minute=0
            )
        )
        print(response.status, response.details)
