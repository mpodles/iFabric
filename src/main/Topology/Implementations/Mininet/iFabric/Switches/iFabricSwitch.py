from mininet.net import Mininet
from mininet.node import Switch, Host
from mininet.moduledeps import pathCheck
from mininet.log import info, error, debug
import tempfile
from time import sleep
import psutil
import os

def check_listening_on_port(port):
    for c in psutil.net_connections(kind='inet'):
        if c.status == 'LISTEN' and c.laddr[1] == port:
            return True
    return False


class MininetSwitch(Switch):
    "BMv2 switch with gRPC support"
    next_grpc_port = 50051
    next_thrift_port = 9090
    next_device_id = 1

    def __init__(self, name, 
                 grpc_port = None,
                 thrift_port = None,
                 pcap_dump = False,
                 log_console = False,
                 verbose = False,
                 device_id = None,
                 enable_debugger = False,
                 log_file = None,
                 **kwargs):
        Switch.__init__(self, name, dpid = str(MininetSwitch.next_device_id), **kwargs)
        MininetSwitch.next_device_id += 1
        
        self.sw_path = "simple_switch_grpc"
        pathCheck(self.sw_path)

        json_path = "/home/mpodles/iFabric/src/main/build/fabric_tunnel.json"

        if json_path is not None:
            # make sure that the provided JSON file exists
            if not os.path.isfile(json_path):
                error("Invalid JSON file: {}\n".format(json_path))
                exit(1)
            self.json_path = json_path
        else:
            self.json_path = None

        if grpc_port is not None:
            self.grpc_port = grpc_port
        else:
            self.grpc_port = MininetSwitch.next_grpc_port
            MininetSwitch.next_grpc_port += 1

        if thrift_port is not None:
            self.thrift_port = thrift_port
        else:
            self.thrift_port = MininetSwitch.next_thrift_port
            MininetSwitch.next_thrift_port += 1

        if check_listening_on_port(self.grpc_port):
            error('%s cannot bind port %d because it is bound by another process\n' % (self.name, self.grpc_port))
            exit(1)

        self.verbose = verbose
        logfile = "/tmp/p4s.{}.log".format(self.name)
        self.output = open(logfile, 'w')
        self.pcap_dump = pcap_dump
        self.enable_debugger = enable_debugger
        self.log_console = log_console
        if log_file is not None:
            self.log_file = log_file
        else:
            self.log_file = "/tmp/p4s.{}.log".format(self.name)
        if device_id is not None:
            self.device_id = device_id
            MininetSwitch.device_id = max(MininetSwitch.device_id, device_id)
        else:
            self.device_id = MininetSwitch.device_id
            MininetSwitch.device_id += 1
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
        args = [self.sw_path]
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

    @classmethod
    def setup(cls):
        pass


class BMVSwitch(MininetSwitch):
    pass