import networkx as nx   
import json
from Topology import Topology
from MininetEndpoint import iFabricEndPoint
from MininetSwitch import BMVSwitch

from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI

   
class SingleSwitch(iFabricTopology):
    def __init__(self):
        self.switch_class = iFabricSwitch
        self.endpoint_class = iFabricEndPoint
        self.endpoints = configuration["endpoints"]
        self.ports_per_endpoint = configuration["ports_per_endpoint"]
        self.avg_group_size =configuration ["avg_group_size"]
        self.mac_addressing = configuration["mac_addressing"]  #is it random or something else
        self.ip_addressing = configuration["ip_addressing"]



    def start_topology(self):
        self.net = Mininet(topo = self.mininet_topo, link = TCLink)
        self.net.start()
        CLI(self.net)
        self.program_nodes()

    def program_nodes(self):
        for node_name in self.endpoints.nodes:
            h = self.net.get(node_name)
            h.cmd("program")
