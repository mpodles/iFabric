import sys 
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton/Communicator')
from OSNetCommunicator import OSNetCommunicator


from Bmv2GrpcUtils import GrpcRequestLogger
from Bmv2GrpcUtils import IterableQueue
import grpc
from p4.v1 import p4runtime_pb2_grpc
from Bmv2GrpcUtils import P4InfoHelper
from mininet.log import info, error, debug
import os


class Bmv2Communicator(OSNetCommunicator):
    def __init__(self, device, **params):
        OSNetCommunicator.__init__(self, device, **params)
        self.add_actions("/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches/Communicator/Actions")
        self.add_states("/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches/Communicator/States")
     
    def connect(self):
        combined_address = str(self.device_data.address)+ ":" + str(self.device_data.grpc_port)
        info("Connecting to P4Runtime server on " +  combined_address)
        self.channel = grpc.insecure_channel(combined_address)
        # if proto_dump_file is not None: #TODO: fix this later
        #     interceptor = GrpcRequestLogger(self.proto_dump_file)
        #     self.channel = grpc.intercept_channel(self.channel, interceptor)
        self.client_stub = p4runtime_pb2_grpc.P4RuntimeStub(self.channel)
        self.requests_stream = IterableQueue()
        self.stream_msg_resp = self.client_stub.StreamChannel(iter(self.requests_stream))

    def disconnect(self):
        self.requests_stream.close()
        self.stream_msg_resp.cancel()

if __name__ == '__main__':
    class a:
        pass
    device = a()
    device.address = "localhost"
    device.grpc_port = 50051
    device.id = 21
    device.p4_json_file_path = '/home/mpodles/iFabric/src/main/build/iFabric_switch.json'
    device.p4info_helper = P4InfoHelper("/home/mpodles/iFabric/src/main/build/iFabric_switch.p4.p4info.txt").p4info


    comm = Bmv2Communicator(device)
    comm.connect()
    comm.take_action("PrepareSwitch")
