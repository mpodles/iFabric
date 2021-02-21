import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches')
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from OSNetDevice import OSNetDevice
from OSNetTopology import OSNetTopology
from mininet.node import Switch
from mininet.link import Link
from mininet.topo import Topo
from Bmv2GrpcSwitch import Bmv2GrpcSwitch
from MininetSwitch import MininetSwitch
from MininetEndpoint import MininetEndpoint
from MininetLink import MininetLink
import os


class MininetTopology(OSNetTopology,Topo):
    def __init__(self,
                switches,
                endpoints,
                links):
                
        Topo.__init__(self)
        OSNetTopology.__init__(self)
        self.switches = switches
        self.endpoints = endpoints
        self.links = links
        self.switch_class = MininetSwitch
        self.switch_constructor_parameters = {}
        self.endpoint_class = MininetEndpoint
        self.endpoint_constructor_parameters = {}
        self.link_class = MininetLink
        self.link_constructor_parameters = {}
        
        
    def generate_mininet_topo(self):
        for endpoint in self.endpoints:
            self.addHost(endpoint, cls=self.endpoint_class, **self.endpoint_constructor_parameters)
        for switch in self.switches:
            self.addSwitch(switch, cls=self.switch_class, **self.switch_constructor_parameters)
        for link in self.links:
            node1,node2 = link[0], link[1]
            self.addLink(node1,node2, cls=self.link_class, **self.link_constructor_parameters)
        
    def generate_nodes(self):
        nodes = []
        for switch in self.switches:
            nodes.append(self.switch_class(switch))

        for endpoint in self.endpoints:
            nodes.append(self.endpoint_class(endpoint))

        return nodes

    def generate_links(self):
        links = []
        for link in self.links:
            links.append(self.link_class(link))

    
class Bmv2GrpcTopo(MininetTopology):
    def __init__(self, switches, endpoints, links, p4runtime_info, p4_json):
        MininetTopology.__init__(self, switches, endpoints, links)
        self.switch_constructor_parameters = {"p4runtime_info":p4runtime_info, "p4_json": p4_json}
        self.switch_class = Bmv2GrpcSwitch


