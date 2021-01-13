import json
import re
import random 
import rstr
import os

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
        self.nodes = []
        self.nodes_with_properties = {}
        self.groups = {}
        self.switches = {}
        self.spines = []
        self.leaves = []
        self.ip_addressing = "random"
        self.mac_addressing = "random"
        self.project_directory = "/home/mpodles/iFabric/src/main"
        self.dir_for_topology = self.project_directory + "/sig-topo"
        self.overlap_groups = True

        self.generate_switches(spines, leaves)
        self.generate_switch_to_switch_links()
        self.generate_nodes_with_links(ports_per_leaf)
        self.generate_groups(avg_group_size)
        self.generate_nodes_addressing()
        self.write_topology()
        

    def generate_switches(self, spines, leaves):
        
        for spine_nr in range (1,spines+1):
            spine = "Spine_" + str(spine_nr)
            self.switches[spine] = {"runtime_json" : "build/" + spine +"-runtime.json"}
            self.spines.append(spine)
            self.links[spine] = {"switchports" : [], "endports": []}
        for leaf_nr in range (1,leaves+1):
            leaf = "Leaf_" + str(leaf_nr)
            self.switches[leaf] = {"runtime_json" : "build/" + leaf +"-runtime.json"}
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
        nodes_iterator = 0
        free_ports = range(ports_per_leaf*len(self.leaves))
        while len(free_ports) > 0:
            nodes_iterator+=1
            node = "Node_" + str(nodes_iterator)
            self.nodes.append(node)
            links, free_ports = self.generate_node_links(1, 3 ,free_ports)
            interface_on_node = 0
            for link in links:
                sw , link = "Leaf_" + str(1 + link/ports_per_leaf), (link%ports_per_leaf) + 1 + len(self.spines)
                self.links[sw]["endports"].append({"port": link, "node": node, "connected_port": interface_on_node })
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
        for node in self.nodes:
            self.nodes_with_properties[node]= {}
            self.nodes_with_properties[node]["ip"] = self.generate_ip_addressing(node)
            self.nodes_with_properties[node]["mac"] = self.generate_mac_addressing(node)
            self.nodes_with_properties[node]["commands"] = self.generate_node_commands(node)


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
        #TODO: change eth0
        return ["ip route add 0.0.0.0/0 dev eth0"]

    def write_topology(self):
        topology = {}

        topology["switches"] = self.switches
        topology["nodes"] = self.nodes_with_properties
        topology["links"] = self.links
        topology["groups"] = self.groups

        topology = json.dumps(topology)

        with open(os.path.join(self.dir_for_topology , 'topology_new.json'),'w+')  as f:
             f.write(topology)



if __name__ == "__main__":
    topology = SpineLeaf(spines = 2, leaves= 4, ports_per_leaf=8, avg_group_size= 4)
    
