import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/iFabric')
from iFabricTopology import iFabricTopology
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/iFabric/TopologiesGenerator')
from TopologyGenerator import SingleSwitchTopologyGenerator
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
class SingleSwitch(iFabricTopology):
    def __init__(self, topology_description_file_path, p4_template_file_path, p4_code_file_path, 
    protocols_description_file_path, protocols_folder_path, 
    p4runtime_info_file_path, p4_json_file_path, 
    log_dir, pcap_dir, **params):

        self.generator = SingleSwitchTopologyGenerator(topology_description_file_path)
        self.generator.generate_topology()
        iFabricTopology.__init__(self,
                                switches = self.generator.switches, 
                                endpoints = self.generator.endpoints,
                                links = self.generator.links, 
                                p4_template_file_path = p4_template_file_path,
                                p4_code_file_path = p4_code_file_path,
                                protocols_description_file_path = protocols_description_file_path,
                                protocols_folder_path = protocols_folder_path,
                                p4runtime_info_file_path = p4runtime_info_file_path, 
                                p4_json_file_path = p4_json_file_path,
                                log_dir = log_dir, 
                                pcap_dir = pcap_dir)
