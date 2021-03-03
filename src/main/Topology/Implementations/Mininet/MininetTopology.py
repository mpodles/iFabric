import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches')
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from OSNetDevice import OSNetDevice
from OSNetTopology import OSNetTopology
from mininet.node import Switch
from mininet.net import Mininet
from mininet.link import Link
from mininet.topo import Topo
from Bmv2GrpcSwitch import Bmv2GrpcSwitch
from MininetSwitch import MininetSwitch
from MininetEndpoint import MininetEndpoint
from MininetLink import MininetLink
import os


class MininetTopology(OSNetTopology):
    def __init__(self,
                switches,
                endpoints,
                links):
                
        # Topo.__init__(self)
        OSNetTopology.__init__(self)
        self.switches = switches
        self.endpoints = endpoints
        self.links = links
        self.switch_class = MininetSwitch
        # self.switch_constructor_parameters = {}
        self.endpoint_class = MininetEndpoint
        # self.endpoint_constructor_parameters = {}
        self.link_class = MininetLink
        # self.link_constructor_parameters = {}
        # self.mininet_topo = None
        self.mininet = None
        
        
    # def generate_mininet_topo(self):
    #     self.mininet_topo = Topo()
    #     for endpoint in self.endpoints.values():
    #         self.mininet_topo.addHost(endpoint.name, cls=self.endpoint_class, params_object = endpoint)
    #     for switch in self.switches.values():
    #         self.mininet_topo.addSwitch(switch.name, cls=self.switch_class, params_object = switch)
    #     for link in self.links.values():
    #         node1,node2 = link.node1.name, link.node2.name
    #         self.mininet_topo.addLink(node1,node2, cls=self.link_class, params_object = link)
    
    def generate_mininet_net(self):
        self.mininet = Mininet(switch = self.switch_class, host = self.endpoint_class, link = self.link_class)
        for endpoint in self.endpoints.values():
            self.mininet.addHost(endpoint.name, cls=self.endpoint_class, params_object = endpoint)
        for switch in self.switches.values():
            self.mininet.addSwitch(switch.name, cls=self.switch_class, params_object = switch)
        for link in self.links.values():
            node1,node2 = link.node1.name, link.node2.name
            self.mininet.addLink(self.mininet.nameToNode[node1],
                                self.mininet.nameToNode[node2], 
                                cls=self.link_class, 
                                params_object = link)
        
    def generate_nodes(self):
        return self.mininet.nameToNode

    def generate_links(self):
        links = {}
        for link in self.mininet.links:
            links[link.link.name] = link
        return links

    def start(self):
        self.mininet.start()

    def run(self):
        self.mininet.start()

    def stop(self):
        self.mininet.stop()

    
class Bmv2GrpcTopo(MininetTopology):
    def __init__(self, switches, endpoints, links, p4_code_file_path, p4runtime_info_file_path, p4_json_file_path, log_dir, pcap_dir):
        MininetTopology.__init__(self, switches, endpoints, links)
        for switch in switches.values():
            switch.p4_json_file_path = p4_json_file_path
            switch.p4runtime_info_file_path = p4runtime_info_file_path
            switch.log_dir = log_dir
            switch.pcap_dir = pcap_dir
        # for endpoint in endpoints.values():

        # for link in links.values():

        self.p4_code_file_path = p4_code_file_path
        self.p4runtime_info_file_path = p4runtime_info_file_path
        self.p4_json_file_path = p4_json_file_path
        self.compile_p4_code()
        # self.switch_constructor_parameters = {"p4runtime_info_path":p4runtime_info_file_path, "p4_json_file_path": p4_json_file_path, "log_dir": log_dir, "pcap_dir": pcap_dir}
        self.switch_class = Bmv2GrpcSwitch
    
    def compile_p4_code(self):
        cmd = "p4c-bm2-ss \
        --p4v 16 \
        --p4runtime-files "+ self.p4runtime_info_file_path +\
        " -o "+ self.p4_json_file_path +\
        " " + self.p4_code_file_path
        os.system(cmd)


