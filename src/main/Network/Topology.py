import networkx as nx   
import json

   
class Topology():
    def __init__(self):
        self.endpoints = nx.Graph()
        self.switches = nx.Graph()
        self.groups = nx.Graph()
        
