import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from MininetSwitch import MininetSwitch
from mininet.moduledeps import pathCheck
from mininet.log import info, error, debug
import tempfile
from time import sleep
import psutil
import os


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
    


    



