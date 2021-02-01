import json
import networkx as nx
from SingleSwitchTopology import SingleSwitchTopology

def initialize_topology(source, **params):
    if source == "generate":
        generate_topology(**params)
    # elif: source == "read":
    #     read_topology()
    # elif: source == "discover":
    #     discover_topology()
        

def generate_topology(topology_configuration_path):
    topology_configuration = json.load(topology_configuration_path)
    topology_type  = topology_configuration["type"]
    if topology_type == "SingleSwitch":
        generated_topology = SingleSwitchTopologyGenerator(topology_configuration)

class TopologyGenerator():
    def __init__(self, configuration):
        self.generate_switches(configuration)
        self.generate_endpoints(configuration)
        self.generate_groups(configuration)

    def generate_switches(self, configuration):
        pass
    
    def generate_endpoints(self, configuration):
        pass

    def generate_groups(self, configuration):
        pass

class SingleSwitchTopologyGenerator(TopologyGenerator):
    def __init__(self, configuration):
        self.topology = SingleSwitchTopology()

        self.endpoints = configuration["endpoints"]
        self.leaves_count = configuration["leaves"]
        self.ports_per_endpoint = configuration["ports_per_endpoint"]
        self.avg_group_size =configuration ["avg_group_size"]
        self.mac_addressing = configuration["mac_addressing"]
        self.ip_addressing = configuration["ip_addressing"]

        self.generate_switches(configuration)
        self.generate_endpoints(configuration)
        self.generate_groups(configuration)

    def generate_switches(self, configuration):
        self.topology.switches.add_node("SingleSwitch")
    
    def generate_endpoints(self, configuration):
        self.topology.endpoints.add_node("SingleSwitch")

    def generate_groups(self, configuration):
        self.topology.groups.add_node("SingleSwitch")