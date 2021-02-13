from mininet.net import Mininet
from mininet.node import Switch, Host
from mininet.moduledeps import pathCheck
from mininet.log import info, error, debug
import tempfile
from time import sleep
import psutil
import os
from Mininet import MininetSwitch

def check_listening_on_port(port):
    for c in psutil.net_connections(kind='inet'):
        if c.status == 'LISTEN' and c.laddr[1] == port:
            return True
    return False


class Bmv2GrpcSwitch(MininetSwitch):
    next_grpc_port = 50051

    def __init__(self, switch):
        Switch.__init__(switch)
        self.compiled_program = switch["compiled_program"]
        
        self.sw_program = "simple_switch_grpc"
        pathCheck(self.sw_program)

        compiled_p4 = switch["compiled_p4_path"]

        if compiled_p4 is not None:
            # make sure that the provided JSON file exists
            if not os.path.isfile(compiled_p4):
                error("Invalid compiled P4 json file: {}\n".format(compiled_p4))
                exit(1)
            self.compiled_p4 = compiled_p4
        else:
            self.compiled_p4 = None


        grpc_port = switch["grpc_port"]
        if grpc_port is not None:
            self.grpc_port = grpc_port
        else:
            self.grpc_port = Bmv2GrpcSwitch.next_grpc_port
            Bmv2GrpcSwitch.next_grpc_port += 1

        if check_listening_on_port(self.grpc_port):
            error('%s cannot bind port %d because it is bound by another process\n' % (self.name, self.grpc_port))
            exit(1)

        logfile = "/tmp/p4s.{}.log".format(self.name)
        self.output = open(logfile, 'w')
        self.pcap_dump = pcap_dump
        self.enable_debugger = enable_debugger
        self.log_console = log_console
        self.device_id = OSNetDevice.OSN_ID
        self.nanomsg = "ipc:///tmp/bm-{}-log.ipc".format(self.device_id)


    def check_switch_started(self, pid):
        for _ in range(10 * 2):
            if not os.path.exists(os.path.join("/proc", str(pid))):
                return False
            if check_listening_on_port(self.grpc_port):
                return True
            sleep(0.5)

    def start(self, controllers):
        info("Starting P4 switch {}.\n".format(self.name))
        args = [self.sw_program]
        for port, intf in self.intfs.items():
            if not intf.IP():
                args.extend(['-i', str(port) + "@" + intf.name])
        if self.pcap_dump:
            args.append("--pcap %s" % self.pcap_dump)
        if self.nanomsg:
            args.extend(['--nanolog', self.nanomsg])
        args.extend(['--device-id', str(self.device_id)])
        MininetSwitch.device_id += 1
        if self.json_path:
            args.append(self.json_path)
        else:
            args.append("--no-p4")
        if self.enable_debugger:
            args.append("--debugger")
        if self.log_console:
            args.append("--log-console")
        if self.thrift_port:
            args.append('--thrift-port ' + str(self.thrift_port))
        if self.grpc_port:
            args.append("-- --grpc-server-addr 0.0.0.0:" + str(self.grpc_port))
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

    def program_switch_p4runtime(self, sw_name, sw_dict, runtimes_files_path, logs_path):
        """ This method will use P4Runtime to program the switch using the
            content of the runtime JSON file as input.
        """
        sw_mn_conn = self.switches_mininet_connections[sw_name]
        grpc_port = sw_mn_conn["grpc_port"]
        device_id = sw_mn_conn["device_id"]
        runtime_json = sw_dict['runtime_json']
        # self.logger('Configuring switch %s using P4Runtime with file %s' % (sw_name, runtime_json))
        with open(os.path.join(runtimes_files_path, runtime_json), 'r') as sw_conf_file:
            outfile = os.path.join(logs_path, sw_name + '-p4runtime-requests.txt')
            self.program_switch(
                sw_name = sw_name,
                addr='127.0.0.1:%d' % grpc_port,
                device_id=device_id,
                sw_conf_file=sw_conf_file,
                workdir=runtimes_files_path,
                proto_dump_fpath=outfile)

    def program_switch(self, sw_name, addr, device_id, sw_conf_file, workdir, proto_dump_fpath):
        sw_conf = self.json_load_byteified(sw_conf_file)
        try:
            self.check_switch_conf(sw_conf=sw_conf, workdir=workdir)
        except ConfException as e:
            error("While parsing input runtime configuration: %s" % str(e))
            return

        info('Using P4Info file %s...' % sw_conf['p4info'])
        p4info_fpath = os.path.join(workdir, sw_conf['p4info'])
        self.p4info_helper = helper.P4InfoHelper(p4info_fpath)

        target = sw_conf['target']

        info("Connecting to P4Runtime server on %s (%s)..." % (addr, target))

        if target == "bmv2":
            sw = bmv2.Bmv2SwitchConnection(name=sw_name, address=addr, device_id=device_id,
                                        proto_dump_file=proto_dump_fpath)
            self.connections[sw_name] = sw
        else:
            raise Exception("Don't know how to connect to target %s" % target)

        sw.MasterArbitrationUpdate()

        if target == "bmv2":
            info("Setting pipeline config (%s)..." % sw_conf['bmv2_json'])
            bmv2_json_fpath = os.path.join(workdir, sw_conf['bmv2_json'])
            sw.SetForwardingPipelineConfig(p4info=self.p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_json_fpath)
        else:
            raise Exception("Should not be here")

        if 'table_entries' in sw_conf:
            table_entries = sw_conf['table_entries']
            info("Inserting %d table entries..." % len(table_entries))
            for entry in table_entries:
                info(self.tableEntryToString(entry))
                self.insertTableEntry(sw, entry)

        if 'multicast_group_entries' in sw_conf:
            group_entries = sw_conf['multicast_group_entries']
            info("Inserting %d group entries..." % len(group_entries))
            for entry in group_entries:
                info(self.groupEntryToString(entry))
                self.insertMulticastGroupEntry(sw, entry)

        if 'clone_session_entries' in sw_conf:
            clone_entries = sw_conf['clone_session_entries']
            info("Inserting %d clone entries..." % len(clone_entries))
            for entry in clone_entries:
                info(self.cloneEntryToString(entry))
                self.insertCloneGroupEntry(sw, entry)
        #     sw.shutdown()

    def insertForwardingRule(self, forwarding_rule):
        pass


    @classmethod
    def setup(cls):
        pass

from Queue import Queue
from abc import abstractmethod
from datetime import datetime

import grpc
from p4.v1 import p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc
from p4.tmp import p4config_pb2

MSG_LOG_MAX_LEN = 1024

# List of all active connections
connections = []

def ShutdownAllSwitchConnections():
    for c in connections:
        c.shutdown()

class SwitchConnection(object):

    def __init__(self, name=None, address='127.0.0.1:50051', device_id=0,
                 proto_dump_file=None):
        self.name = name
        self.address = address
        self.device_id = device_id
        self.p4info = None
        self.channel = grpc.insecure_channel(self.address)
        if proto_dump_file is not None:
            interceptor = GrpcRequestLogger(proto_dump_file)
            self.channel = grpc.intercept_channel(self.channel, interceptor)
        self.client_stub = p4runtime_pb2_grpc.P4RuntimeStub(self.channel)
        self.requests_stream = IterableQueue()
        self.stream_msg_resp = self.client_stub.StreamChannel(iter(self.requests_stream))
        self.proto_dump_file = proto_dump_file
        connections.append(self)

    @abstractmethod
    def buildDeviceConfig(self, **kwargs):
        return p4config_pb2.P4DeviceConfig()

    def shutdown(self):
        self.requests_stream.close()
        self.stream_msg_resp.cancel()

    def MasterArbitrationUpdate(self, dry_run=False, **kwargs):
        request = p4runtime_pb2.StreamMessageRequest()
        request.arbitration.device_id = self.device_id
        request.arbitration.election_id.high = 0
        request.arbitration.election_id.low = 1

        if dry_run:
            print "P4Runtime MasterArbitrationUpdate: ", request
        else:
            self.requests_stream.put(request)
            for item in self.stream_msg_resp:
                return item # just one

    def SetForwardingPipelineConfig(self, p4info, dry_run=False, **kwargs):
        device_config = self.buildDeviceConfig(**kwargs)
        request = p4runtime_pb2.SetForwardingPipelineConfigRequest()
        request.election_id.low = 1
        request.device_id = self.device_id
        config = request.config

        config.p4info.CopyFrom(p4info)
        config.p4_device_config = device_config.SerializeToString()

        request.action = p4runtime_pb2.SetForwardingPipelineConfigRequest.VERIFY_AND_COMMIT
        if dry_run:
            print "P4Runtime SetForwardingPipelineConfig:", request
        else:
            self.client_stub.SetForwardingPipelineConfig(request)

    def WriteTableEntry(self, table_entry, dry_run=False, modify=False):
        request = p4runtime_pb2.WriteRequest()
        request.device_id = self.device_id
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
        request.device_id = self.device_id
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
        request.device_id = self.device_id
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
        request.device_id = self.device_id
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

class GrpcRequestLogger(grpc.UnaryUnaryClientInterceptor,
                        grpc.UnaryStreamClientInterceptor):
    """Implementation of a gRPC interceptor that logs request to a file"""

    def __init__(self, log_file):
        self.log_file = log_file
        with open(self.log_file, 'w') as f:
            # Clear content if it exists.
            f.write("")

    def log_message(self, method_name, body):
        with open(self.log_file, 'a') as f:
            ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            msg = str(body)
            f.write("\n[%s] %s\n---\n" % (ts, method_name))
            if len(msg) < MSG_LOG_MAX_LEN:
                f.write(str(body))
            else:
                f.write("Message too long (%d bytes)! Skipping log...\n" % len(msg))
            f.write('---\n')

    def intercept_unary_unary(self, continuation, client_call_details, request):
        self.log_message(client_call_details.method, request)
        return continuation(client_call_details, request)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        self.log_message(client_call_details.method, request)
        return continuation(client_call_details, request)

class IterableQueue(Queue):
    _sentinel = object()

    def __iter__(self):
        return iter(self.get, self._sentinel)

    def close(self):
        self.put(self._sentinel)
