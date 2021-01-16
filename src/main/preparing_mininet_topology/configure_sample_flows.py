import json 
import random 

class FlowGenerator():

    def __init__(self, **files):
        topology_file_path = files["topology_file_path"]
        self.read_topology(topology_file_path)

    def read_topology(self, topology_file_path):
        with open(topology_file_path, 'r') as f:
            topo = json.load(f)
            self.switches = topo['switches']
            self.groups = topo['groups']
            self.nodes = topo['nodes']
            self.topology = topo['links']
            self.nodes_links = topo['node_links']

class DestinationFlowGenerator(FlowGenerator):

    def __init__(self, **files):
        FlowGenerator.__init__(self, **files)
        
    