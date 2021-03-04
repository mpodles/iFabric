import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from MininetSwitch import MininetSwitch
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches/Communicator')
from Bmv2Communicator import Bmv2Communicator
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
        self.p4_json_file_path = self.device.p4_json_file_path
        self.p4runtime_info_file_path = self.device.p4runtime_info_file_path
        self.log_dir = self.device.log_dir
        self.pcap_dir = self.device.pcap_dir

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
        self.address = "127.0.0.1"
        try: 
            self.grpc_port = self.device.grpc_port
        except:
            self.grpc_port = Bmv2GrpcSwitch.next_grpc_port
            Bmv2GrpcSwitch.next_grpc_port += 1

        if self.check_listening_on_port():
            error('%s cannot bind port %d because it is bound by another process\n' % (self.device.name, self.grpc_port))
            exit(1)
        self.log_file = "/tmp/p4s.{}.log".format(self.device.name)
        self.output = open(self.log_file, 'w')
        self.pcap_dump = True
        self.enable_debugger = True
        self.log_console = True
        self.nanomsg = "ipc:///tmp/bm-{}-log.ipc".format(self.OSN_ID)

    
    def run(self):
        self.start()

    def start(self, controllers=None):
        info("Starting P4 switch {}.\n".format(self.device.name))
        args = [self.sw_program]
        # for port, intf in self.intfs.items():
        #     if not intf.IP():
        #         args.extend(['-i', str(port) + "@" + intf.name])
        # if self.pcap_dump:
        #     args.append("--pcap %s" % self.pcap_dump)
        # if self.nanomsg:
        #     args.extend(['--nanolog', self.nanomsg])
        args.extend(['--device-id', str(self.OSN_ID)])
        if self.p4_json_file_path:
            args.append(self.p4_json_file_path)
        else:
            args.append("--no-p4")
        # if self.enable_debugger:
        #     args.append("--debugger")
        # if self.log_console:
        #     args.append("--log-console")
        if self.grpc_port:
            args.append("-- --grpc-server-addr " + str(self.address) +":"+ str(self.grpc_port))
        cmd = ' '.join(args)
        info(cmd + "\n")
        pid = None
        self.cmd(cmd + " &")
        # with tempfile.NamedTemporaryFile() as f:
        #     self.cmd(cmd + ' >' + self.log_file + ' 2>&1 & echo $! >> ' + f.name)
        #     pid = int(f.read())
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
        output = self.cmd("netstat --listen | grep " + str(self.grpc_port))
        if "LISTEN" in output and str(self.grpc_port) in output:
            return True #TODO: do something with this xd
        # for c in psutil.net_connections(kind='inet'):
        #     if c.status == 'LISTEN' and c.laddr[1] == self.grpc_port:
        #         return True
        return False
    


    



