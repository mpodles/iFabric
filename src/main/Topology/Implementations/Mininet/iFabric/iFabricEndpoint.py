import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from MininetEndpoint import MininetEndpoint

class iFabricEndpoint(MininetEndpoint):
    def __init__(self, name, **params):
        MininetEndpoint.__init__(self, name, **params)

    def config(self, **params):
        # r = MininetEndpoint.__init__(**params)
        for interface, int_config in self.device.interfaces.items():
            mac = int_config["mac"] 
            ip = int_config["ip"]
            self.setMAC(mac, intf=interface)
            self.setIP(ip, intf=interface)
        # return r