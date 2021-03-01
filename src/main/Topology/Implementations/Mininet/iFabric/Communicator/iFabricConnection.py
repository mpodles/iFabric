import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches/Communicator')
from Bmv2Connection import Bmv2Connection
from Bmv2GrpcUtils import GrpcRequestLogger
from Bmv2GrpcUtils import IterableQueue
from p4.tmp import p4config_pb2
import grpc
from p4.v1 import p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc
from Bmv2GrpcUtils import P4InfoHelper
from mininet.log import info, error, debug
class iFabricConnection(Bmv2Connection):
    def __init__(self, communicator):
        Bmv2Connection.__init__(self, communicator)
        
    