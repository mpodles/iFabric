import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from MininetEndpoint import MininetEndpoint

sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/iFabric/Communicator')
from HostCommunicator import HostCommunicator

class iFabricEndpoint(MininetEndpoint):
    def __init__(self, name, **params):
        MininetEndpoint.__init__(self, name, **params)
        self.OSNetCommunicator_class = HostCommunicator

    def config(self, **params):
        # r = MininetEndpoint.__init__(**params)
        for interface, int_config in self.device_data.interfaces.items():
            mac = int_config["mac"] 
            ip = int_config["ip"]
            self.setMAC(mac, intf=interface)
            self.setIP(ip, intf=interface)
        # return r