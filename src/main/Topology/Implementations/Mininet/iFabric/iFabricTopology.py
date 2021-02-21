import sys
import os
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from construct_p4_new import P4Constructor
from MininetTopology import Bmv2GrpcTopo

from iFabricEndpoint import iFabricEndpoint
from iFabricSwitch import iFabricSwitch
from iFabricLink import iFabricLink

class iFabricTopology(Bmv2GrpcTopo):

    def __init__(self, switches, endpoints, links, p4_template_file_path, **kwargs):
        self.p4_template_file_path = p4_template_file_path
        self.p4_constructor = P4Constructor(p4_template_file_path)
        Bmv2GrpcTopo.__init__(self, switches, endpoints, links, **kwargs)
        self.switch_class = iFabricSwitch
        self.endpoint_class = iFabricEndpoint
        self.link_class = iFabricLink


        
        



        