import json
import rstr
import random
import networkx as nx
from Topology import  Topology
from SingleSwitchTopology import SingleSwitchTopology
from MininetSwitch import MininetSwitch
from MininetEndpoint import iFabricEndPoint

def initialize_topology(source, *params):
    if source == "generate":
        return generate_topology(*params)
    # elif: source == "read":
    #     read_topology()
    # elif: source == "discover":
    #     discover_topology()
        

def generate_topology(topology_configuration_path):
    topology_configuration = json.loads(open(topology_configuration_path).read())
    topology_type  = topology_configuration["type"]
    if topology_type == "SingleSwitch":
        return SingleSwitchTopologyGenerator(topology_configuration).generate_topology()
    

class TopologyGenerator(object):
    def __init__(self, configuration):
        self.topology = Topology()
       

    def generate_topology(self):
        self.generate_switches()
        self.generate_endpoints()
        self.generate_groups()
        self.generate_topology_with_endpoints()
        self.generate_topology_with_groups()
        return self.topology
    
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

class SingleSwitchTopologyGenerator(TopologyGenerator):
    def __init__(self, configuration):
        super(SingleSwitchTopologyGenerator, self).__init__(configuration)
        self.topology = SingleSwitchTopology()

        self.endpoints = configuration["endpoints"]
        self.ports_per_endpoint = configuration["ports_per_endpoint"]
        self.avg_group_size =configuration ["avg_group_size"]
        self.mac_addressing = configuration["mac_addressing"]  #is it random or something else
        self.ip_addressing = configuration["ip_addressing"]

    def generate_topology(self):
        self.generate_switches()
        self.generate_endpoints()
        self.generate_groups()

        self.generate_topology_with_endpoints()
        #self.generate_topology_with_groups()

        return self.topology

    def generate_switches(self):
        self.topology.switches.add_node("SingleSwitch")
        self.topology.mininet_topo.addSwitch(
            "SingleSwitch", 
            cls=self.topology.switch_class)
    
    def generate_endpoints(self):
        for ep_nr in range(1,self.endpoints+1):
            endpoint_name = "EP_" + str(ep_nr)
            self.topology.endpoints.add_node(endpoint_name)
            self.topology.mininet_topo.addNode(
                endpoint_name)

    def generate_groups(self):
        groups_count = self.endpoints / self.avg_group_size
        for gr_nr in range(1, groups_count + 1):
            endpoints = ["EP_" + str(self.avg_group_size*gr_nr - i) for i in range(self.avg_group_size)]
            self.topology.groups.add_node("Group_" + str(gr_nr), endpoints = endpoints)

    def generate_topology_with_endpoints(self):
        switch_interface = 1
        for endpoint in self.topology.endpoints.nodes:
            info = {"cls" : self.topology.endpoint_class}
            interfaces = {}
            for endpoint_interface in range(self.ports_per_endpoint):
                switch_interface += 1
                self.topology.mininet_topo.addLink(
                    "SingleSwitch",
                    endpoint, 
                    delay='0ms',
                    bw=None,
                    port1=switch_interface,
                    port2=endpoint_interface)
                interface_name = endpoint + "-eth" + str(endpoint_interface)
                interfaces[interface_name] = {
                    "ip": self.generate_ip_addressing(endpoint),
                    "mac": self.generate_mac_addressing(endpoint),
                    "connected_to": "SingleSwitch",
                    "connected_on": switch_interface}
                    
            info["interfaces"] = interfaces
            self.topology.mininet_topo.setNodeInfo(endpoint, info = info)

            self.topology.switches_with_endpoints.add_edge(
                    "SingleSwitch",
                    endpoint, 
                    weight=1, 
                    interfaces= interfaces)

    def generate_topology_with_groups(self):
        #TODO: finish this
        switch_interface = 1
        # for group in self.topology.groups.nodes:
        #     for endpoint_interface in range(self.ports_per_endpoint):
        #         self.topology.switches_with_endpoints.add_edge(
        #             "SingleSwitch",
        #             group, 
        #             weight=1, 
        #             interfaces= [{"SingleSwitch": switch_interface , endpoint: endpoint_interface}])

    
    def generate_ip_addressing(self, endpoint):
        if self.ip_addressing == "random":
            return self.generate_random_ip_addressing()

    def generate_random_ip_addressing(self):
        return str(random.randint(10, 223)) + "." + str(random.randint(0, 255))+ "." +str(random.randint(0, 255))+ "." +str(random.randint(0, 255))

    def generate_mac_addressing(self, endpoint):
        if self.ip_addressing == "random":
            return self.generate_random_mac_addressing()

    def generate_random_mac_addressing(self):
        #TODO: verify rstr licence
        random_mac=rstr.xeger('[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]')
        return random_mac
    