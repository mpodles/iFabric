import sys
import os
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from construct_p4_new import P4Constructor
from MininetTopology import Bmv2GrpcTopo

from iFabricEndpoint import iFabricEndpoint
from iFabricSwitch import iFabricSwitch
from iFabricLink import iFabricLink

class iFabricTopology(Bmv2GrpcTopo):

    def __init__(self, switches, endpoints, links, 
        p4_template_file_path,
        protocols_description_file_path,
        protocols_folder_path,
        p4_code_file_path,
        p4runtime_info_file_path, 
        p4_json_file_path,
        log_dir, 
        pcap_dir, 
        **kwargs):

        self.p4_template_file_path = p4_template_file_path
        self.p4_constructor = P4Constructor(
            protocols_folder_path = protocols_folder_path,
            protocols_description_file_path = protocols_description_file_path,
            template_file_path = p4_template_file_path,
            p4_file_target_path = p4_code_file_path
        )
        Bmv2GrpcTopo.__init__(self, switches, endpoints, links, 
        p4runtime_info_file_path = p4runtime_info_file_path, 
        p4_code_file_path = p4_code_file_path,
        p4_json_file_path = p4_json_file_path,
        log_dir = log_dir, 
        pcap_dir = pcap_dir, 
        **kwargs)
        self.switch_class = iFabricSwitch
        self.endpoint_class = iFabricEndpoint
        self.link_class = iFabricLink


        
        



        