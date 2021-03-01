import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton/Communicator')
from OSNetConnection import OSNetConnection
from OSNetAction import OSNetAction
from OSNetState import OSNetState

from Bmv2GrpcUtils import GrpcRequestLogger
from Bmv2GrpcUtils import IterableQueue
from p4.tmp import p4config_pb2
import grpc
from p4.v1 import p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc
from Bmv2GrpcUtils import P4InfoHelper
from mininet.log import info, error, debug
import os

from importlib import import_module

class Bmv2Connection(OSNetConnection):
    def __init__(self,communicator):
        OSNetConnection.__init__(self,communicator)
        self.add_actions()
        self.add_states()

    def add_actions(self):
        for filename in os.listdir("./Actions"):
            module = import_module(filename, "Actions")
            self.OSN_Actions.append(OSNetAction(filename, module.perform_action))
    
    def add_states(self):
        for filename in os.listdir("./States"):
            module = import_module(filename, "States")
            self.OSN_State.append(OSNetState(filename, module.get_function()))
     
    def connect(self):
        combined_address = str(self.address)+ ":" + str(self.grpc_port)
        info("Connecting to P4Runtime server on " +  combined_address)
        self.channel = grpc.insecure_channel(combined_address)
        if self.proto_dump_file is not None:
            interceptor = GrpcRequestLogger(self.proto_dump_file)
            self.channel = grpc.intercept_channel(self.channel, interceptor)
        self.client_stub = p4runtime_pb2_grpc.P4RuntimeStub(self.channel)
        self.requests_stream = IterableQueue()
        self.stream_msg_resp = self.client_stub.StreamChannel(iter(self.requests_stream))

    def disconnect(self):
        self.requests_stream.close()
        self.stream_msg_resp.cancel()