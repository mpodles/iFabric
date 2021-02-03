from mininet.net import Mininet
from mininet.node import Switch, Host

class MininetEndpoint(Host):
    def config(self, **params):
        return super(MininetEndpoint, self).config(**params)


class iFabricEndPoint(MininetEndpoint):
    def config(self, **params):
        r = super(iFabricEndPoint, self).config(**params)
        for interface, int_config in params["interfaces"].items():
            interface_name = self.name+"-eth" + str(interface) 
            mac = int_config["mac"] 
            ip = int_config["ip"]
            self.setMAC(mac, intf=interface_name)
            self.setIP(ip, intf=interface_name)
        return r

