from iFabric import iFabricEndPoint

class iFabricMainframe(iFabricEndPoint):
    def config(self, **params):
        r = MininetEndpoint.__init__(**params)
        for interface, int_config in params["interfaces"].items():
            interface_name = self.name+"-eth" + str(interface) 
            mac = int_config["mac"] 
            ip = int_config["ip"]
            self.setMAC(mac, intf=interface_name)
            self.setIP(ip, intf=interface_name)
        return r