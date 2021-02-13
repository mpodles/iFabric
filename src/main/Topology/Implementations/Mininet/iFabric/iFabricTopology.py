from Mininet import MininetTopology
from Mininet.Switches import Bmv2GrpcSwitch
import os

class iFabricTopology(MininetTopology):

    def __init__(self,files):
        MininetTopology.__init__(switch_class = iFabricSwitch, endpoint_class = iFabricEndPoint, link_class = iFabricLink)

        compiled_p4 =  files["compiled_p4"] #"./fabric_tunnel_compiled.json"

        self.groups = {}