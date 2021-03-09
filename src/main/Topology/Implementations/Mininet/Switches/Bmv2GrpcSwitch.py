import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from MininetSwitch import MininetSwitch
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches/Communicator')
from Bmv2Communicator import Bmv2Communicator
from Bmv2GrpcUtils import P4InfoHelper
from mininet.moduledeps import pathCheck
from mininet.log import info, error, debug
import tempfile
from time import sleep
import psutil



class Bmv2GrpcSwitch(MininetSwitch):
    next_grpc_port = 50051

    def __init__(self, switch, **params):
        MininetSwitch.__init__(self, switch, **params)
        self.OSNetCommunicator_class = Bmv2Communicator
        self.device.sw_program = "simple_switch_grpc"
        pathCheck(self.device.sw_program)

        try:
            self.device.address = self.device.address
        except:
            self.device.address = "localhost"

        try: 
            self.device.grpc_port = self.device.grpc_port
        except:
            self.device.grpc_port = Bmv2GrpcSwitch.next_grpc_port
            Bmv2GrpcSwitch.next_grpc_port += 1

        if self.check_listening_on_port():
            error('%s cannot bind port %d because it is bound by another process\n' % (self.device.name, self.device.grpc_port))
            exit(1)
        self.device.log_file = "/tmp/p4s.{}.log".format(self.device.name)
        self.output = open(self.device.log_file, 'w')
        self.device.pcap_dump = True
        self.device.enable_debugger = True
        self.device.log_console = True
        self.device.nanomsg = "ipc:///tmp/bm-{}-log.ipc".format(self.device.id)
        self.device.p4info_helper = P4InfoHelper("/home/mpodles/iFabric/src/main/build/iFabric_switch.p4.p4info.txt")
 
    def run(self):
        self.start()

    def start(self, controllers=None):
        info("Starting P4 switch {}.\n".format(self.device.name))
        # self.cmd("ip link set lo up")
        # self.cmd("ip link set lo address A0:A0:AB:AB:AB:AB")
        args = [self.device.sw_program]
        for port, intf in self.intfs.items():
            if not intf.IP():
                args.extend(['-i', str(port) + "@" + intf.name])
        # if self.pcap_dump:
        #     args.append("--pcap %s" % self.pcap_dump)
        # if self.nanomsg:
        #     args.extend(['--nanolog', self.nanomsg])
        args.extend(['--device-id', str(self.device.id)])
        print self.device.id
        if self.device.p4_json_file_path:
            args.append(self.device.p4_json_file_path)
        else:
            args.append("--no-p4")
        # if self.enable_debugger:
        #     args.append("--debugger")
        # if self.log_console:
        #     args.append("--log-console")
        if self.device.grpc_port:
            args.append("-- --grpc-server-addr " + str(self.device.address) +":"+ str(self.device.grpc_port))
        cmd = ' '.join(args)
        info(cmd + "\n")
        pid = None
        # self.cmd(cmd + " &")
        with tempfile.NamedTemporaryFile() as f:
            self.cmd(cmd + ' >' + self.device.log_file + ' 2>&1 & echo $! >> ' + f.name)
            self.device.pid = int(f.read())
        # debug("P4 switch {} PID is {}.\n".format(self.device.name, pid))
        if not self.check_switch_started(pid):
            error("P4 switch {} did not start correctly.\n".format(self.device.name))
            exit(1)
        info("P4 switch {} has been started.\n".format(self.device.name))


    def check_switch_started(self, pid):
        for _ in range(10 * 2):
            # if not os.path.exists(os.path.join("/proc", str(pid))):
            #     return False
            if self.check_listening_on_port():
                return True
            sleep(0.5)
    
    def check_listening_on_port(self):
        output = self.cmd("netstat --listen | grep " + str(self.device.grpc_port))
        if "LISTEN" in output and str(self.device.grpc_port) in output:
            return True #TODO: do something with this xd
        # for c in psutil.net_connections(kind='inet'):
        #     if c.status == 'LISTEN' and c.laddr[1] == self.grpc_port:
        #         return True
        return False
    


    



