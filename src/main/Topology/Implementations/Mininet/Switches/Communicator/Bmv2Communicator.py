import sys 
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton/Communicator')
from OSNetCommunicator import OSNetCommunicator

from Bmv2Connection import Bmv2Connection

from Bmv2GrpcUtils import GrpcRequestLogger
from Bmv2GrpcUtils import IterableQueue
from p4.tmp import p4config_pb2
import grpc
from p4.v1 import p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc
from Bmv2GrpcUtils import P4InfoHelper
from mininet.log import info, error, debug

class Bmv2Communicator(OSNetCommunicator):
    def __init__(self,  **params):
        OSNetCommunicator.__init__(self)
        self.connections.append(Bmv2Connection("grpc",self))
        self.OSN_States.append(self.ReadTableEntries)
        self.ID = ID
        self.address = address
        self.grpc_port = grpc_port
        self.p4info_helper = P4InfoHelper(p4runtime_info_file_path)
        self.p4_json_file_path = p4_json_file_path
        self.proto_dump_file = params.get("proto_dump_file", None)
        

