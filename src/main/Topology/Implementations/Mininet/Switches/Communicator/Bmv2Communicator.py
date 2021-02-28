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
    def __init__(self, switch, address, ID, grpc_port, p4runtime_info_file_path, p4_json_file_path, **params):
        OSNetCommunicator.__init__(self)
        self.ID = ID
        self.address = address
        self.grpc_port = grpc_port
        self.p4info_helper = P4InfoHelper(p4runtime_info_file_path)
        self.p4_json_file_path = p4_json_file_path
        self.proto_dump_file = params.get("proto_dump_file", None)
        


    def ReadTableEntries(self, table_id=None, dry_run=False):
        request = p4runtime_pb2.ReadRequest()
        request.device_id = self.ID
        entity = request.entities.add()
        table_entry = entity.table_entry
        if table_id is not None:
            table_entry.table_id = table_id
        else:
            table_entry.table_id = 0
        if dry_run:
            print "P4Runtime Read:", request
        else:
            for response in self.client_stub.Read(request):
                yield response

    def ReadCounters(self, counter_id=None, index=None, dry_run=False):
        request = p4runtime_pb2.ReadRequest()
        request.device_id = self.ID
        entity = request.entities.add()
        counter_entry = entity.counter_entry
        if counter_id is not None:
            counter_entry.counter_id = counter_id
        else:
            counter_entry.counter_id = 0
        if index is not None:
            counter_entry.index.index = index
        if dry_run:
            print "P4Runtime Read:", request
        else:
            for response in self.client_stub.Read(request):
                yield response
