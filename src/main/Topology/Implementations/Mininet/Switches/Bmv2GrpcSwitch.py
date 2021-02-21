import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from MininetSwitch import MininetSwitch
from mininet.moduledeps import pathCheck
from mininet.log import info, error, debug
import tempfile
from time import sleep
import psutil
import os
from Bmv2GrpcUtils import GrpcRequestLogger
from Bmv2GrpcUtils import IterableQueue
from p4.tmp import p4config_pb2
import grpc
from p4.v1 import p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc
from Bmv2GrpcUtils import P4InfoHelper

class Bmv2GrpcSwitch(MininetSwitch):
    next_grpc_port = 50051

    def __init__(self, switch, p4_json_file_path, p4runtime_info_file_path, log_dir, pcap_dir, **params):
        MininetSwitch.__init__(self, switch, **params)
        self.p4_json_file_path = p4_json_file_path
        self.p4runtime_info_file_path = p4runtime_info_file_path
        self.log_dir = log_dir
        self.pcap_dir = pcap_dir

        self.sw_program = "simple_switch_grpc"
        pathCheck(self.sw_program)
        # if compiled_p4 is not None:
        #     # make sure that the provided JSON file exists
        #     if not os.path.isfile(compiled_p4):
        #         error("Invalid compiled P4 json file: {}\n".format(compiled_p4))
        #         exit(1)
        #     self.compiled_p4 = compiled_p4
        # else:
        #     self.compiled_p4 = None

        self.p4info_helper = P4InfoHelper(self.p4runtime_info_file_path)
        grpc_port = params.get("grpc_port",None)
        self.address= '0.0.0.0'
        if grpc_port is not None:
            self.grpc_port = grpc_port
        else:
            self.grpc_port = Bmv2GrpcSwitch.next_grpc_port
            Bmv2GrpcSwitch.next_grpc_port += 1

        if self.check_listening_on_port():
            error('%s cannot bind port %d because it is bound by another process\n' % (self.name, self.grpc_port))
            exit(1)
        logfile = "/tmp/p4s.{}.log".format(self.name)
        self.output = open(logfile, 'w')
        # self.pcap_dump = pcap_dump
        # self.enable_debugger = enable_debugger
        # self.log_console = log_console
        
        self.nanomsg = "ipc:///tmp/bm-{}-log.ipc".format(self.device_id)

    
    def run(self):
        self.start()

    def start(self):
        info("Starting P4 switch {}.\n".format(self.name))
        args = [self.sw_program]
        for port, intf in self.intfs.items():
            if not intf.IP():
                args.extend(['-i', str(port) + "@" + intf.name])
        if self.pcap_dump:
            args.append("--pcap %s" % self.pcap_dump)
        if self.nanomsg:
            args.extend(['--nanolog', self.nanomsg])
        args.extend(['--device-id', str(self.ID)])
        if self.p4_json_file_path:
            args.append(self.p4_json_path)
        else:
            args.append("--no-p4")
        if self.enable_debugger:
            args.append("--debugger")
        if self.log_console:
            args.append("--log-console")
        if self.grpc_port:
            args.append("-- --grpc-server-addr " + str(self.address) +":"+ str(self.grpc_port))
        cmd = ' '.join(args)
        info(cmd + "\n")
        pid = None
        with tempfile.NamedTemporaryFile() as f:
            self.cmd(cmd + ' >' + self.log_file + ' 2>&1 & echo $! >> ' + f.name)
            pid = int(f.read())
        debug("P4 switch {} PID is {}.\n".format(self.name, pid))
        if not self.check_switch_started(pid):
            error("P4 switch {} did not start correctly.\n".format(self.name))
            exit(1)
        info("P4 switch {} has been started.\n".format(self.name))


    def check_switch_started(self, pid):
        for _ in range(10 * 2):
            if not os.path.exists(os.path.join("/proc", str(pid))):
                return False
            if self.check_listening_on_port():
                return True
            sleep(0.5)
    
    def check_listening_on_port(self):
        for c in psutil.net_connections(kind='inet'):
            if c.status == 'LISTEN' and c.laddr[1] == self.grpc_port:
                return True
        return False

    def get_switch_ready(self):
        info("Connecting to P4Runtime server on " +  str(self.address) +":"+ str(self.grpc_port))
        switch_connection = self.connect_to_switch()

        switch_connection.MasterArbitrationUpdate()

        switch_connection.SetForwardingPipelineConfig()

    def connect_to_switch(self):
        self.connection = self.SwitchConnection(self)

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
        self.connection.WriteTableEntry(table_entry)
    
    def modifyTableEntry(self, flow):
        table_entry = self.build_table_entry(flow)
        self.connection.WriteTableEntry(table_entry, modify=True)


    # @classmethod
    # def setup(cls):
    #     pass

    class SwitchConnection(object):
        def __init__(self, switch):
            self.switch = switch
            self.channel = grpc.insecure_channel(str(switch.address)+ ":" + str(switch.grpc_port))
            if switch.proto_dump_file is not None:
                interceptor = GrpcRequestLogger(switch.proto_dump_file)
                self.channel = grpc.intercept_channel(self.channel, interceptor)
            self.client_stub = p4runtime_pb2_grpc.P4RuntimeStub(self.channel)
            self.requests_stream = IterableQueue()
            self.stream_msg_resp = self.client_stub.StreamChannel(iter(self.requests_stream))
            
        def shutdown(self):
            self.requests_stream.close()
            self.stream_msg_resp.cancel()

        def MasterArbitrationUpdate(self, dry_run=False, **kwargs):
            request = p4runtime_pb2.StreamMessageRequest()
            request.arbitration.device_id = self.switch.OSN_ID
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
            request.device_id = self.switch.OSN_ID
            config = request.config

            config.p4info.CopyFrom(self.switch.p4info)
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
            device_config.device_data = self.switch.p4_json_file_path
            return device_config

        def WriteTableEntry(self, table_entry, dry_run=False, modify=False):
            request = p4runtime_pb2.WriteRequest()
            request.device_id = self.OSN_ID
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

        def ReadTableEntries(self, table_id=None, dry_run=False):
            request = p4runtime_pb2.ReadRequest()
            request.device_id = self.OSN_ID
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
            request.device_id = self.OSN_ID
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


        def WritePREEntry(self, pre_entry, dry_run=False, modify=False):
            request = p4runtime_pb2.WriteRequest()
            request.device_id = self.OSN_ID
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


    



