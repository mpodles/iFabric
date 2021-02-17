from Mininet import BMV2GrpcTopo
from Mininet.Switches import Bmv2GrpcSwitch
import os

class iFabricTopology(BMV2GrpcTopo):

    def __init__(self,files):
        BMV2GrpcTopo.__init__()
        self.switch_class = iFabricSwitch
        self.endpoint_class = iFabricEndPoint
        self.link_class = iFabricLink

        compiled_p4 =  files["compiled_p4"] #"./fabric_tunnel_compiled.json"
        self.groups = {}
        