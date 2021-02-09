import networkx as nx   
import json
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
   
class Topology(object):
    def __init__(self):
        self.endpoints = nx.Graph()
        self.switches = nx.Graph()
        self.groups = nx.Graph()
        self.switches_with_endpoints = nx.Graph()
        self.switches_with_groups = nx.Graph()
        self.switch_class = None
        self.endpoint_class = None
        self.mininet_topo = Topo()

        
