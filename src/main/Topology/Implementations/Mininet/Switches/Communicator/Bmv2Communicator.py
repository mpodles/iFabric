import sys 
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton/Communicator')
from OSNetCommunicator import OSNetCommunicator

from Bmv2GrpcUtils import GrpcRequestLogger
from Bmv2GrpcUtils import IterableQueue
from p4.tmp import p4config_pb2
import grpc
from p4.v1 import p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc
from Bmv2GrpcUtils import P4InfoHelper
from mininet.log import info, error, debug

class Bmv2Communicator(OSNetCommunicator):
    def __init__(self, address, ID, grpc_port, p4runtime_info_file_path, p4_json_file_path, **params):
        OSNetCommunicator.__init__(self)
        self.ID = ID
        self.address = address
        self.grpc_port = grpc_port
        self.p4info_helper = P4InfoHelper(p4runtime_info_file_path)
        self.p4_json_file_path = p4_json_file_path
        self.proto_dump_file = params.get("proto_dump_file", None)
        
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

    def get_switch_ready(self):
        self.MasterArbitrationUpdate()
        self.SetForwardingPipelineConfig()

    def MasterArbitrationUpdate(self, dry_run=False, **kwargs):
        request = p4runtime_pb2.StreamMessageRequest()
        request.arbitration.device_id = self.ID
        request.arbitration.election_id.high = 0
        request.arbitration.election_id.low = 1

        if dry_run:
            print "P4Runtime MasterArbitrationUpdate: ", request
        else:
            self.requests_stream.put(request)
            for item in self.stream_msg_resp:
                return item # just one

    def SetForwardingPipelineConfig(self, dry_run=False):
        device_config = self.buildDeviceConfig()
        request = p4runtime_pb2.SetForwardingPipelineConfigRequest()
        request.election_id.low = 1
        request.device_id = self.ID
        config = request.config

        config.p4info.CopyFrom(self.p4info_helper)
        config.p4_device_config = device_config.SerializeToString()

        request.action = p4runtime_pb2.SetForwardingPipelineConfigRequest.VERIFY_AND_COMMIT
        if dry_run:
            print "P4Runtime SetForwardingPipelineConfig:", request
        else:
            self.client_stub.SetForwardingPipelineConfig(request)

    def buildDeviceConfig(self):
        "Builds the device config for BMv2"
        device_config = p4config_pb2.P4DeviceConfig()
        device_config.reassign = True
        device_config.device_data = self.p4_json_file_path
        return device_config

    def build_table_entry(self, flow):
        table_name = flow['table']
        match_fields = flow.get('match') # None if not found
        action_name = flow['action_name']
        default_action = flow.get('default_action') # None if not found
        action_params = flow['action_params']
        priority = flow.get('priority')  # None if not found

        table_entry = self.p4info_helper.buildTableEntry(
            table_name=table_name,
            match_fields=match_fields,
            default_action=default_action,
            action_name=action_name,
            action_params=action_params,
            priority=priority)
        
        return table_entry
    
    def insertTableEntry(self, flow):
        table_entry = self.build_table_entry(flow)
        self.WriteTableEntry(table_entry)
    
    def modifyTableEntry(self, flow):
        table_entry = self.build_table_entry(flow)
        self.WriteTableEntry(table_entry, modify=True)
            

    def WriteTableEntry(self, table_entry, dry_run=False, modify=False):
        request = p4runtime_pb2.WriteRequest()
        request.device_id = self.ID
        request.election_id.low = 1
        update = request.updates.add()
        if table_entry.is_default_action or modify:
            update.type = p4runtime_pb2.Update.MODIFY
        else:
            update.type = p4runtime_pb2.Update.INSERT
        update.entity.table_entry.CopyFrom(table_entry)
        if dry_run:
            print "P4Runtime Write:", request
        else:
            self.client_stub.Write(request)

    def WritePREEntry(self, pre_entry, dry_run=False, modify=False):
        request = p4runtime_pb2.WriteRequest()
        request.device_id = self.ID
        request.election_id.low = 1
        update = request.updates.add()
        if modify:
            update.type = p4runtime_pb2.Update.MODIFY
        else:
            update.type = p4runtime_pb2.Update.INSERT
        update.entity.packet_replication_engine_entry.CopyFrom(pre_entry)
        if dry_run:
            print "P4Runtime Write Multicast:", request
        else:
            # print "Writing entry", request
            self.client_stub.Write(request)

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

    def disconnect(self):
        self.requests_stream.close()
        self.stream_msg_resp.cancel()