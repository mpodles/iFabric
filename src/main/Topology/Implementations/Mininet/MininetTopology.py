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
        self.endpoint_class = MininetEndpoint
        self.link_class = MininetLink
        
        
    def generate_mininet_topo(self):
        for endpoint in self.endpoints:
            self.addHost(endpoint, cls=self.endpoint_class)
        for switch in self.switches:
            self.addSwitch(switch, cls=self.switch_class)
        for link in self.links:
            node1,node2 = link[0], link[1]
            self.addLink(node1,node2, cls=self.link_class)
        
    def generate_nodes(self):
        nodes = []
        for switch in self.switches:
            nodes.append(OSNetDevice(device = switch))

        for endpoint in self.endpoints:
            nodes.append(self.endpoint_class(endpoint))

        return nodes

    def generate_links(self):
        links = []
        for link in self.links:
            links.append(OSNetLink(link = link))

        for endpoint in self.endpoints:
            nodes.append(self.endpoint_class(endpoint))

        return nodes



    
class BMV2GrpcTopo(MininetTopology):
    def __init__(self, switches, endpoints, links, **params):
        MininetTopology.__init__(self, switches, endpoints, links)
        self.log_dir = params["log_dir"]
        self.pcap_dir = params["pcap_dir"]
        
        self.p4_code_path = params["p4_code_path"]
        self.p4_json_path = params["p4_json_path"]
        self.p4runtime_info_path = params["p4runtime_info_path"]

        self.switch_class = Bmv2GrpcSwitch

        self.add_switches(switches)
        self.add_nodes(nodes)
        self.add_links(links, node_links)

    def generate_p4_code(self):
        cmd = "p4c-bm2-ss \
        --p4v 16 \
        --p4runtime-files "+ self.p4runtime_info +\
        " -o "+ self.p4_json +\
        " " + self.p4_code_path
        os.system(cmd)


    def add_switches(self, switches):
        for sw, params in switches.iteritems():
            self.addSwitch(sw, cls=Bmv2GrpcSwitch)
    
    def add_nodes(self, nodes):
        for node, interfaces in nodes.items():
            self.addNode(node, cls= MininetEndpoint)


    def add_links(self, switch_links, node_links):
        for node, links in node_links.items():
            for node_link in links:
                self.addLink(node, sw,
                         delay='0ms', bw=None,
                         port1=node_port, port2=sw_port)

        for sw, links in switch_links.items():
            for switch_link in links["switchports"]:
                self.addLink(sw, connected_sw,
                        port1=sw_port, port2=connected_sw_port,
                        delay='0ms', bw=None)