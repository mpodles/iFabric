import json
import sys # Library for INT_MAX 
import re
import networkx as nx
from networkx.algorithms import approximation

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

class  MinimalSpanningTreeRules(ForwardingRules):

    def __init__(self, links, node_links, flows, policy):
        ForwardingRules.__init__(self, links, node_links, flows, policy)
        # self.graph_nodes_ids = {}
        # self.generate_ids() 
        # self.graph = MinimalSpanningTreeRules.Graph(self.number_of_graph_nodes) 
        # self.parse_links_into_graph()
        # self.graph.primMST()
        # pass        

        self.G = nx.Graph()
        for switch, switch_connections in self.links.items():
            for connections in switch_connections["switchports"]:
                connected_switch = connections["connected_switch"]
                self.G.add_edge(
                    switch,
                    connected_switch
                )
        for policy_entry in self.policy:  
            source_switches, destination_switches = self.parse_policy_entry(policy_entry)

            in_first = set(source_switches)
            in_second = set(destination_switches)

            in_second_but_not_in_first = in_second - in_first

            terminal_nodes = source_switches + list(in_second_but_not_in_first)
            steiner_tree = approximation.steinertree.steiner_tree(self.G, terminal_nodes)
            pass

            
    def parse_policy_entry(self, policy_entry):
        if policy_entry["type"] == "F2NI":
                source_switches = self.links.keys()
                destination = policy_entry["destination"]
                destination_interface = policy_entry["interface"]
                destination_switches = self.get_destination_nodes(destination, destination_interface)
                return source_switches, destination_switches


    def get_destination_nodes(self, destination, destination_interface = None):
        nodes = []
        if destination_interface is not None:
            for interface_connections in self.node_links[destination]:
                if interface_connections["port"] == int(destination_interface):
                    nodes.append(interface_connections["connected_switch"]) 
            return nodes
        else:
            for interface_connections in self.node_links[destination]:
                nodes.append(interface_connections["connected_switch"])             
        return nodes


    # def prepare_graph(self, source_switches, destination_switches, non_edge_switches):
    #     pass

    # def _reverse(self, graph):
    #     r = {}
    #     for src in graph:
    #         for (dst,c) in graph[src].items():
    #             if dst in r:
    #                 r[dst][src] = c
    #             else:
    #                 r[dst] = { src : c }
    #     return r

    # def _getCycle(self, n, g, visited=None, cycle=None):
    #     if visited is None:
    #         visited = set()
    #     if cycle is None:
    #         cycle = []
    #     visited.add(n)
    #     cycle += [n]
    #     if n not in g:
    #         return cycle
    #     for e in g[n]:
    #         if e not in visited:
    #             cycle = self._getCycle(e,g,visited,cycle)
    #     return cycle

    # def _mergeCycles(self, cycle,G,RG,g,rg):
    #     allInEdges = []
    #     minInternal = None
    #     minInternalWeight = sys.maxint

    #     # find minimal internal edge weight
    #     for n in cycle:
    #         for e in RG[n]:
    #             if e in cycle:
    #                 if minInternal is None or RG[n][e] < minInternalWeight:
    #                     minInternal = (n,e)
    #                     minInternalWeight = RG[n][e]
    #                     continue
    #             else:
    #                 allInEdges.append((n,e))        

    #     # find the incoming edge with minimum modified cost
    #     minExternal = None
    #     minModifiedWeight = 0
    #     for s,t in allInEdges:
    #         u,v = rg[s].popitem()
    #         rg[s][u] = v
    #         w = RG[s][t] - (v - minInternalWeight)
    #         if minExternal is None or minModifiedWeight > w:
    #             minExternal = (s,t)
    #             minModifiedWeight = w

    #     u,w = rg[minExternal[0]].popitem()
    #     rem = (minExternal[0],u)
    #     rg[minExternal[0]].clear()
    #     if minExternal[1] in rg:
    #         rg[minExternal[1]][minExternal[0]] = w
    #     else:
    #         rg[minExternal[1]] = { minExternal[0] : w }
    #     if rem[1] in g:
    #         if rem[0] in g[rem[1]]:
    #             del g[rem[1]][rem[0]]
    #     if minExternal[1] in g:
    #         g[minExternal[1]][minExternal[0]] = w
    #     else:
    #         g[minExternal[1]] = { minExternal[0] : w }

    # # --------------------------------------------------------------------------------- #

    # def mst(self, root,G):
    #     """ The Chu-Lui/Edmond's algorithm
    #     arguments:
    #     root - the root of the MST
    #     G - the graph in which the MST lies
    #     returns: a graph representation of the MST
    #     Graph representation is the same as the one found at:
    #     http://code.activestate.com/recipes/119466/
    #     Explanation is copied verbatim here:
    #     The input graph G is assumed to have the following
    #     representation: A vertex can be any object that can
    #     be used as an index into a dictionary.  G is a
    #     dictionary, indexed by vertices.  For any vertex v,
    #     G[v] is itself a dictionary, indexed by the neighbors
    #     of v.  For any edge v->w, G[v][w] is the length of
    #     the edge.  This is related to the representation in
    #     <http://www.python.org/doc/essays/graphs.html>
    #     where Guido van Rossum suggests representing graphs
    #     as dictionaries mapping vertices to lists of neighbors,
    #     however dictionaries of edges have many advantages
    #     over lists: they can store extra information (here,
    #     the lengths), they support fast existence tests,
    #     and they allow easy modification of the graph by edge
    #     insertion and removal.  Such modifications are not
    #     needed here but are important in other graph algorithms.
    #     Since dictionaries obey iterator protocol, a graph
    #     represented as described here could be handed without
    #     modification to an algorithm using Guido's representation.
    #     Of course, G and G[v] need not be Python dict objects;
    #     they can be any other object that obeys dict protocol,
    #     for instance a wrapper in which vertices are URLs
    #     and a call to G[v] loads the web page and finds its links.
    #     """

    #     RG = self._reverse(G)
    #     if root in RG:
    #         RG[root] = {}
    #     g = {}
    #     for n in RG:
    #         if len(RG[n]) == 0:
    #             continue
    #         minimum = sys.maxint
    #         s,d = None,None
    #         for e in RG[n]:
    #             if RG[n][e] < minimum:
    #                 minimum = RG[n][e]
    #                 s,d = n,e
    #         if d in g:
    #             g[d][s] = RG[s][d]
    #         else:
    #             g[d] = { s : RG[s][d] }
                
    #     cycles = []
    #     visited = set()
    #     for n in g:
    #         if n not in visited:
    #             cycle = self._getCycle(n,g,visited)
    #             cycles.append(cycle)

    #     rg = self._reverse(g)
    #     for cycle in cycles:
    #         if root in cycle:
    #             continue
    #         self._mergeCycles(cycle, G, RG, g, rg)

    #     return g
    # # def generate_ids(self):
    # #     node_id = 0
    # #     for switch, ports in self.links.items():
    # #         if switch not in self.graph_nodes_ids:
    # #             self.graph_nodes_ids[switch] = node_id 
    # #             node_id += 1
    # #         for switchport in ports["switchports"]: 
    # #             connected_switch = switchport["connected_switch"]
    # #             if connected_switch not in self.graph_nodes_ids:
    # #                 self.graph_nodes_ids[connected_switch] = node_id 
    # #                 node_id += 1
    # #         for endport in ports["endports"]:
    # #             node = endport["node"] + "_" + str(endport["connected_port"])
    # #             if node not in self.graph_nodes_ids:
    # #                 self.graph_nodes_ids[node] = node_id 
    # #                 node_id += 1

    # #     self.number_of_graph_nodes = len(self.graph_nodes_ids)

    # # def parse_links_into_graph(self):
    # #     for switch, ports in self.links.items():
    # #         for switchport in ports["switchports"]: 
    # #             port = switchport["port"]
    # #             connected_switch = switchport["connected_switch"]
    # #             connected_port = switchport["connected_port"]
    # #             switch_id = self.graph_nodes_ids[switch]
    # #             connected_switch_id = self.graph_nodes_ids[connected_switch]
    # #             self.graph.graph[switch_id][connected_switch_id] = 1
    # #             self.graph.graph[connected_switch_id][switch_id] = 1

    # #         for endport in ports["endports"]:
    # #             port = endport["port"]
    # #             nodeport = endport["connected_port"]
    # #             node = endport["node"] + "_" + str(nodeport)
    # #             node_id = self.graph_nodes_ids[node]
    # #             self.graph.graph[switch_id][node_id] = 1
    # #             self.graph.graph[node_id][switch_id] = 1
                


                


        
    
    # # #Taken from https://www.geeksforgeeks.org/prims-minimum-spanning-tree-mst-greedy-algo-5/
    # # class Graph(): 
    
    # #     def __init__(self, vertices): 
    # #         self.V = vertices 
    # #         self.graph = [[-1 for _ in range(vertices)]  
    # #                     for _ in range(vertices)] 
    
    # #     # A utility function to print the constructed MST stored in parent[] 
    # #     def printMST(self, parent): 
    # #         print "Edge \tWeight"
    # #         for i in range(1, self.V): 
    # #             print parent[i], "-", i, "\t", self.graph[i][ parent[i] ] 
    
    # #     # A utility function to find the vertex with  
    # #     # minimum distance value, from the set of vertices  
    # #     # not yet included in shortest path tree 
    # #     def minKey(self, key, mstSet): 
    
    # #         # Initilaize min value 
    # #         min = sys.maxint 
    
    # #         for v in range(self.V): 
    # #             if key[v] < min and mstSet[v] == False: 
    # #                 min = key[v] 
    # #                 min_index = v 
    
    # #         return min_index 
    
    # #     # Function to construct and print MST for a graph  
    # #     # represented using adjacency matrix representation 
    # #     def primMST(self): 
    
    # #         # Key values used to pick minimum weight edge in cut 
    # #         key = [sys.maxint] * self.V 
    # #         parent = [None] * self.V # Array to store constructed MST 
    # #         # Make key 0 so that this vertex is picked as first vertex 
    # #         key[0] = 0 
    # #         mstSet = [False] * self.V 
    
    # #         parent[0] = -1 # First node is always the root of 
    
    # #         for _ in range(self.V): 
    
    # #             # Pick the minimum distance vertex from  
    # #             # the set of vertices not yet processed.  
    # #             # u is always equal to src in first iteration 
    # #             u = self.minKey(key, mstSet) 
    
    # #             # Put the minimum distance vertex in  
    # #             # the shortest path tree 
    # #             mstSet[u] = True
    
    # #             # Update dist value of the adjacent vertices  
    # #             # of the picked vertex only if the current  
    # #             # distance is greater than new distance and 
    # #             # the vertex in not in the shotest path tree 
    # #             for v in range(self.V): 
    
    # #                 # graph[u][v] is non zero only for adjacent vertices of m 
    # #                 # mstSet[v] is false for vertices not yet included in MST 
    # #                 # Update the key only if graph[u][v] is smaller than key[v] 
    # #                 if self.graph[u][v] > 0 and mstSet[v] == False and key[v] > self.graph[u][v]: 
    # #                         key[v] = self.graph[u][v] 
    # #                         parent[v] = u 
    
    # #         self.printMST(parent) 
    
    
    # # # Contributed by Divyanshu Mehta 

    
    
