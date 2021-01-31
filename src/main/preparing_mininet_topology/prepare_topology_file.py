import json
import re
import random 
import rstr
import os

#TODO: Make it also prepare mininet topology itself, not only file to parse

def choose_topology(structure):
    return SpineLeaf

class Topology():
    pass
    #TODO: Make general Topology interface or use the mininet Topo

class SpineLeaf():
    #TODO: Decouple hosts from topology and generate them however You wish

    def __init__(self, configuration, topology_target_path):
        spines_count = configuration["spines"]
        leaves_count = configuration["leaves"]
        ports_per_leaf = configuration["ports_per_leaf"]
        avg_group_size =configuration ["avg_group_size"]
        self.topology_target_path = topology_target_path
        self.topology = {}
        self.links = {}
        self.nodes = []
        self.nodes_with_properties = {}
        self.node_links = {}
        self.groups = {}
        self.switches = {}
        self.spines = []
        self.leaves = []
        self.ip_addressing = configuration["ip_addressing"]
        self.mac_addressing = configuration["mac_addressing"]
        self.overlap_groups = bool(configuration["overlap_groups"])

        self.generate_switches(spines_count, leaves_count)
        self.generate_switch_to_switch_links()
        #self.generate_nodes_with_links(ports_per_leaf)
        self.generate_one_node_per_leaf(nr_of_interfaces=1)
        self.generate_groups(avg_group_size)
        self.generate_nodes_addressing()
        self.write_topology()
        

    def generate_switches(self, spines_count, leaves_count):
        for spine_nr in range (1,spines_count+1):
            spine = "Spine_" + str(spine_nr)
            self.switches[spine] = {"runtime_json" : spine +"-runtime.json"}
            self.spines.append(spine)
            self.links[spine] = {"switchports" : [], "endports": []}
        for leaf_nr in range (1,leaves_count+1):
            leaf = "Leaf_" + str(leaf_nr)
            self.switches[leaf] = {"runtime_json" : leaf +"-runtime.json"}
            self.leaves.append(leaf)
            self.links[leaf] = {"switchports" : [], "endports": []}

    def generate_switch_to_switch_links(self):
        leaf_interface = 1
        for spine in self.spines:
            spine_interface = 1
            for leaf in self.leaves:
                self.links[leaf]["switchports"].append({"port": leaf_interface, "connected_switch": spine, "connected_port": spine_interface })
                self.links[spine]["switchports"].append({"port": spine_interface, "connected_switch": leaf, "connected_port": leaf_interface })
                spine_interface += 1 
            leaf_interface += 1

    def generate_one_node_per_leaf(self, nr_of_interfaces):
        nodes_iterator = 0
        for leaf in self.leaves:
            nodes_iterator+=1
            node = "Node_" + str(nodes_iterator)
            self.nodes.append(node)
            self.node_links[node] = []
            link = 1 + len(self.spines)
            interface_on_node = 0 
            while interface_on_node < nr_of_interfaces:
                self.links[leaf]["endports"].append({"port": link, "node": node, "connected_port": interface_on_node })
                self.node_links[node].append({"port": interface_on_node, "connected_switch": leaf, "connected_port": link })
                interface_on_node +=1
                link +=1
                

    def generate_nodes_with_links(self, ports_per_leaf):
        #Generate random number of nodes based on how many endports are available
        nodes_iterator = 0
        free_ports = range(ports_per_leaf*len(self.leaves))
        while len(free_ports) > 0:
            nodes_iterator+=1
            node = "Node_" + str(nodes_iterator)
            self.nodes.append(node)
            self.node_links[node] = []
            links, free_ports = self.generate_node_links(1, 3 ,free_ports)
            interface_on_node = 0
            for link in links:
                sw , link = "Leaf_" + str(1 + link/ports_per_leaf), (link%ports_per_leaf) + 1 + len(self.spines)
                self.links[sw]["endports"].append({"port": link, "node": node, "connected_port": interface_on_node })
                self.node_links[node].append({"port": interface_on_node, "connected_switch": sw, "connected_port": link })
                interface_on_node += 1
          

    def generate_node_links(self, min_links_per_node, max_links_per_node, free_ports):
        how_many_ports = min(random.randint(min_links_per_node, max_links_per_node), len(free_ports))
        subset = random.sample(free_ports, how_many_ports)
        free_ports_left = [port for port in free_ports if port not in subset]
        return subset, free_ports_left

    
    def generate_groups(self, avg_group_size):
        ungrouped_nodes = range(len(self.nodes))
        group_id = 1
        while len(ungrouped_nodes) > 0:
            sample_length = min(avg_group_size, len(ungrouped_nodes))
            subset = random.sample(ungrouped_nodes, sample_length)
            group = "Group_" + str(group_id)
            self.groups[group] = [self.nodes[i] for i in subset]
            if self.overlap_groups:
                how_many_to_delete = random.randint(0, sample_length)
                while how_many_to_delete > 0:
                    subset.pop(0)
                    how_many_to_delete -=1
                ungrouped_nodes = [node for node in ungrouped_nodes if node not in subset]
            else:
                ungrouped_nodes = [node for node in ungrouped_nodes if node not in subset]
            group_id +=1
        for group, nodes in self.groups.items():
            if len(nodes) <=1:
                self.groups.pop(group)

    def generate_nodes_addressing(self):
        for node, connections in self.node_links.items():
            self.nodes_with_properties[node]= {} 
            self.nodes_with_properties[node]["commands"] = self.generate_node_commands(node)
            for connection in connections:
                port = connection["port"]
                self.nodes_with_properties[node][port] = {}
                self.nodes_with_properties[node][port]["ip"] = self.generate_ip_addressing(node)
                self.nodes_with_properties[node][port]["mac"] = self.generate_mac_addressing(node)
               


    def generate_ip_addressing(self, node):
        if self.ip_addressing == "random":
            return self.generate_random_ip_addressing()

    def generate_random_ip_addressing(self):
        return str(random.randint(10, 223)) + "." + str(random.randint(0, 255))+ "." +str(random.randint(0, 255))+ "." +str(random.randint(0, 255))

    def generate_mac_addressing(self, node):
        if self.ip_addressing == "random":
            return self.generate_random_mac_addressing()

    def generate_random_mac_addressing(self):
        #TODO: verify rstr licence
        random_mac=rstr.xeger('[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]')
        return random_mac

    def generate_node_commands(self, node):
        return ["ip route add 0.0.0.0/0 dev "+ node + "-eth0"]

    def write_topology(self):
        topology = {}

        topology["switches"] = self.switches
        topology["nodes"] = self.nodes_with_properties
        topology["links"] = self.links
        topology["node_links"] = self.node_links
        topology["groups"] = self.groups

        topology = json.dumps(topology)

        with open(self.topology_target_path,'w+')  as f:
             f.write(topology)



if __name__ == "__main__":
    pass
    #topology = SpineLeaf(spines = 2, leaves= 4, ports_per_leaf=8, avg_group_size= 4)
    
