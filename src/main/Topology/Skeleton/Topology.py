import networkx as nx   
import json


class Topology(object):
    def __init__(self):
        self.endpoints = {}
        self.switches = {}
        self.groups = {}
        self.graphs = {}
       

    def generate_topology(self):
        self.generate_switches()
        self.generate_endpoints()
        self.generate_groups()
        self.generate_topology_with_endpoints()
        self.generate_topology_with_groups()
    
    def generate_switches(self):
        pass
    
    def generate_endpoints(self):
        pass

    def generate_groups(self):
        pass

    def generate_topology_with_endpoints(self):
        pass

    def generate_topology_with_groups(self):
        pass
   
# class Topology_old(object):
#     def __init__(self):
#         self.endpoints = nx.Graph()
#         self.switches = nx.Graph()
#         self.groups = nx.Graph()
#         self.switches_with_endpoints = nx.Graph()
#         self.switches_with_groups = nx.Graph()
#         self.switch_class = None
#         self.endpoint_class = None
#         self.mininet_topo = Topo()
#         self.topology = Topology()
       

#     def generate_topology(self):
#         self.generate_switches()
#         self.generate_endpoints()
#         self.generate_groups()
#         self.generate_topology_with_endpoints()
#         self.generate_topology_with_groups()
#         return self.topology
    
#     def generate_switches(self):
#         pass
    
#     def generate_endpoints(self):
#         pass

#     def generate_groups(self):
#         pass

#     def generate_topology_with_endpoints(self):
#         pass

#     def generate_topology_with_groups(self):
#         pass

        
