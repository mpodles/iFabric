import json
import re
import random 

class Topology():
    def generate_switches(self):
        pass

    def generate_nodes(self):
        pass
    
    def generate_links(self):
        pass

    def generate_groups(self):
        pass

    def generate_flows(self):
        pass

    def generate_policy(self):
        pass

    def parse_policy_into_flows(self):
        pass

class SpineLeaf():

    def __init__(self, spines = 2, leaves= 4, ports_per_leaf=8, avg_group_size = 4):
        self.topology = {}
        self.links = {}
        self.groups = {}
        self.generate_switches(spines, leaves)
        self.generate_switch_to_switch_links()
        self.generate_nodes_with_links(ports_per_leaf)
        self.generate_groups(avg_group_size)
        

    def generate_switches(self, spines, leaves):
        self.switches = []
        self.spines = []
        self.leaves = []
        for spine_nr in range (1,spines+1):
            spine = "Spine_" + str(spine_nr)
            self.switches.append(spine)
            self.spines.append(spine)
            self.links[spine] = {"switchports" : [], "endports": []}
        for leaf_nr in range (1,leaves+1):
            leaf = "Leaf_" + str(leaf_nr)
            self.switches.append(leaf)
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

    def generate_nodes_with_links(self, ports_per_leaf):
        #Generate random number of nodes based on how many endports are available
        self.nodes = []
        nodes_iterator = 0
        free_ports = range(ports_per_leaf*len(self.leaves))
        while len(free_ports) > 0:
            nodes_iterator+=1
            node = "Node_" + str(nodes_iterator)
            self.nodes.append(node)
            links, free_ports = self.generate_node_links(1, 3 ,free_ports)
            for link in links:
                interface_on_node = 0
                sw , link = "Leaf_" + str(1 + link/ports_per_leaf), (link%ports_per_leaf) + 1 + len(self.spines)
                self.links[sw]["endports"].append({"port": link, "node": node, "connected_port": interface_on_node })
                interface_on_node += 1
          

    def generate_node_links(self, min_links_per_node, max_links_per_node, free_ports):
        how_many_ports = min(random.randint(min_links_per_node, max_links_per_node), len(free_ports))
        subset = random.sample(free_ports, how_many_ports)
        free_ports_left = [port for port in free_ports if port not in subset]
        return subset, free_ports_left

    
    def generate_groups(self, avg_group_size, overlap = True):
        ungrouped_nodes = range(len(self.nodes))
        group_id = 1
        while len(ungrouped_nodes) > 0:
            sample_length = min(avg_group_size, len(ungrouped_nodes))
            subset = random.sample(ungrouped_nodes, sample_length)
            group = "Group_" + str(group_id)
            self.groups[group] = [self.nodes[i] for i in subset]
            if overlap:
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

    def generate_ip_addressing(self):
        pass

    def generate_mac_addressing(self):
        pass
    


if __name__ == "__main__":
    topology = SpineLeaf(spines = 2, leaves= 4, ports_per_leaf=8, avg_group_size= 4)
    print topology.nodes
    print
    print topology.links
    print
    print topology.groups
