import sys
import os
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from MininetTopology import Bmv2GrpcTopo

from iFabricEndpoint import iFabricEndpoint
from iFabricSwitch import iFabricSwitch
from iFabricLink import iFabricLink

class iFabricTopology(Bmv2GrpcTopo):

    def __init__(self, switches, endpoints, links, p4_code_path, p4runtime_info_path, p4_json_path):
        Bmv2GrpcTopo.__init__(self, switches, endpoints, links, p4runtime_info_path, p4_json_path)
        self.p4_code_path = p4_code_path
        self.p4runtime_info = p4runtime_info_path
        self.p4_json = p4_json_path
        self.switch_class = iFabricSwitch
        self.endpoint_class = iFabricEndpoint
        self.link_class = iFabricLink

    def generate_p4_code(self):
        cmd = "p4c-bm2-ss \
        --p4v 16 \
        --p4runtime-files "+ self.p4runtime_info +\
        " -o "+ self.p4_json +\
        " " + self.p4_code_path
        os.system(cmd)
        
        



        