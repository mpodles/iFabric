from iFabric import iFabricEndpoint

class iFabricMainframe(iFabricEndpoint):
    def config(self, **params):
        r = iFabricEndpoint.__init__(**params)
        for interface, int_config in params["interfaces"].items():
            interface_name = self.name+"-eth" + str(interface) 
            mac = int_config["mac"] 
            ip = int_config["ip"]
            self.setMAC(mac, intf=interface_name)
            self.setIP(ip, intf=interface_name)
        return r