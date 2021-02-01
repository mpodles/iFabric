import networkx as nx   
import json
from Topology import Topology

   
class SingleSwitchTopology(Topology):
    def __init__(self):
        self.endpoints = nx.Graph()
        self.switches = nx.Graph()
        self.groups = nx.Graph()
        
