import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from MininetEndpoint import MininetEndpoint

class iFabricEndpoint(MininetEndpoint):
    def __init__(self, name, **params):
        self.name = name

    def config(self, **params):
        r = MininetEndpoint.__init__(**params)
        for interface, int_config in params["interfaces"].items():
            interface_name = self.name+"-eth" + str(interface) 
            mac = int_config["mac"] 
            ip = int_config["ip"]
            self.setMAC(mac, intf=interface_name)
            self.setIP(ip, intf=interface_name)
        return r