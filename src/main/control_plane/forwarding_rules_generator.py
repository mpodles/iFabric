import json
import sys # Library for INT_MAX 
import re
import networkx as nx
from networkx.algorithms import approximation
import copy

class ForwardingRules():
    def __init__(self, links, node_links, flows, policy):
        self.links = links
        self.node_links = node_links
        self.flows = flows
        self.policy = policy

    def get_multicast_rules(self):
        rules = {}
        for sw, _ in self.links.items():
            rules[sw] = self.get_rules_for_sw(sw)
        return rules
            
    def get_rules_for_sw(self, sw):
        rules_of_sw = []
        for flow_name, flow_id in self.flows.items():
                rules_of_sw.append(self.get_rule_for_flow_for_sw(flow_id, sw))
        return rules_of_sw
    
    def get_rule_for_flow_for_sw(self, flow_id, sw):
        if "Leaf_1" in sw:
            rule = {
            "multicast_group_id" : flow_id,
            "replicas" : [
            {
                "egress_port" : 1,
                "instance" : 1
            }
            ]
        }

        if "Leaf_2" in sw:
            rule = {
            "multicast_group_id" : flow_id,
            "replicas" : [
            {
                "egress_port" : 2,
                "instance" : 2
            }
            ]
        }

        if "Spine" in sw:
            rule = {
            "multicast_group_id" : flow_id,
            "replicas" : [
            {
                "egress_port" : 2,
                "instance" : 2
            }
            ]
        }
            
        return rule

class  DestinationPortsRules(ForwardingRules):

    def __init__(self, links, node_links, flows, policy):
        ForwardingRules.__init__(self, links, node_links, flows, policy)
        # self.graph_nodes_ids = {}
        # self.generate_ids() 
        # self.graph = MinimalSpanningTreeRules.Graph(self.number_of_graph_nodes) 
        # self.parse_links_into_graph()
        # self.graph.primMST()
        # pass  
        # 
        self.graph = nx.Graph()

        self.generate_topology_as_nx_graph()
        self.get_edmonds_trees()


    def generate_topology_as_nx_graph(self):
        self.add_all_inter_switch_edges()
        #self.add_all_edges_from_switches_to_nodes()

    def add_all_inter_switch_edges(self):
        for switch, switch_connections in self.links.items():
            for connections in switch_connections["switchports"]:
                port, connected_port, connected_switch = connections["port"], connections["connected_port"], connections["connected_switch"]
                self.graph.add_edge(switch, connected_switch, weight=1, interfaces= {switch:port , connected_switch: connected_port})

    # def add_all_edges_from_switches_to_nodes(self):   #TODO: in the future maybe it's better to disjont all nodes interfaces and treat like separate nodes for path builiding
    #     for policy_entry in self.policy:
    #         source_switches = self.get_source_switches()
    #         destination_node = policy_entry["destination"]
    #         destination_interface = policy_entry["interface"]
    #         destination_switch, destination_switch_port = self.get_destination_switch(destination_node, destination_interface)
    #         destination_node_
    #         for switch in source_switches:
    #             self.graph.add_edge(switch, destination_node + "_" + destination_interfaces, weight=1, interfaces= {switch:port , connected_switch: connected_port})


    # def parse_policy_entry(self, policy_entry):
    #     policy_type = policy_entry["type"]
    #     if policy_type == "F2N":
    #         pass
        # elif policy_type == "N2N":  #TODO: different policy types in the future
        #     pass

    def get_source_switches(self):
        return self.links.keys()

 
    # def get_steiner_trees(self):
    #     for (flow1,flow2) in self.flows.items():
    #         source_switches, destination_switches = self.parse_policy_entry(policy_entry)
    #         terminal_nodes = source_switches | destination_switches
    #         steiner_tree = approximation.steinertree.steiner_tree(self.G, terminal_nodes)
            

    # def get_destination_nodes(self, destination, destination_interfaces = None):
    #     nodes = []
    #     nodes_interfaces = {}
    #     if destination_interfaces is not None:
    #         for interface_connections in self.node_links[destination]:
    #             if interface_connections["port"] == int(destination_interfaces):
    #                 nodes_interfaces[interface_connections["connected_switch"]] = interface_connections["connected_port"]
    #         return nodes_interfaces
    #     else:
    #         for interface_connections in self.node_links[destination]:

    #             nodes_interfaces[interface_connections["connected_switch"]] = interface_connections["connected_port"]            
    #     return nodes

    def get_edmonds_trees(self):
        for policy_entry in self.policy:
            new_graph = copy.deepcopy(self.graph)
            source_switches = self.get_source_switches()
            destination_node = policy_entry["destination"]
            destination_interface = policy_entry["interface"]
            destination_switch, destination_switch_port = self.get_destination_switch(destination_node, destination_interface)
            destination_node_name = destination_node + "_" + destination_interface
            
            new_graph.add_edge(destination_switch, destination_node_name , weight=1, 
            interfaces= {destination_switch : destination_switch_port , destination_node_name: destination_interface})

            edmond = nx.algorithms.tree.branchings.Edmonds(new_graph)
            edmond.find_optimum()

            terminal_nodes = source_switches
            steiner_tree = approximation.steinertree.steiner_tree(new_graph, terminal_nodes)
            print steiner_tree

    def get_destination_switch(self, destination_node, destination_interface):
        for link in self.node_links[destination_node]:
            if str(link["port"]) == destination_interface:
                return link["connected_switch"], link["connected_port"]
        

    