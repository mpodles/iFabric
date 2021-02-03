import networkx as nx   
import json
from Topology import Topology
from MininetEndpoint import iFabricEndPoint
from MininetSwitch import BMVSwitch

from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo
from mininet.link import TCLink

   
class SingleSwitchTopology(Topology):
    def __init__(self):
        super(SingleSwitchTopology, self).__init__()
        self.switch_class = BMVSwitch
        self.endpoint_class = iFabricEndPoint

    def start_topology(self):
        self.net.start()
        self.program_nodes()

    def program_nodes(self):
        for node_name in self.endpoints.nodes:
            h = self.net.get(node_name)
            h.cmd("program")
