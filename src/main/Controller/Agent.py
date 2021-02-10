import concurrent.futures
import subprocess
import os
import jinja2
import random

class Agent(object):

    def __init__(self, topology, other_agents):
        self.topology = topology
        self.other_agents = other_agents
    

    def start(self):
        try:
            self.initialize_operation()
            self.operate()
            self.close_operation()
        except Exception as e:
            print e
        finally:
            self.close_operation()
    
    def initialize_operation(self):
        print "Initializing operation"

    def operate(self):
        pass

    def close_operation(self):
        pass


class iFabricMainframe(Agent):

    def __init__(self,topology,other_agents):
        super(iFabricMainframe,self).__init__(topology,other_agents)
        self.topology_template_path = topology
        print self.topology, "kolejne"
        self.other_agents = other_agents
        self.initialize_operation()
        

    def initialize_operation(self):
        self.terminals_per_tree = self.prepare_policy_trees()
        self.graph = self.get_topology_graph()


    def prepare_policy_trees(self):
        terminal_nodes = {}
        for i in range (500):
            terminal_nodes[i]= self.get_terminal_nodes()
        return terminal_nodes

    def get_terminal_nodes(self):
        sample_length = 70
        subset = random.sample([host for host in range(16,416)], sample_length)
        return {"length":len(subset), "nodes": subset}


    def get_topology_graph(self):
        spines = 5
        leaves = 10
        hosts_per_leaf = 40
        nodes = spines + leaves + leaves*hosts_per_leaf
        links = spines*leaves + leaves*hosts_per_leaf
        spine_to_leaf_links =\
        {(spine,leaf+spines):1 for spine in range(1,spines+1) for leaf in range(1,leaves+1)}

        leaf_to_hosts_links =\
        {(leaf+spines, leaves+spines +(leaf-1)*hosts_per_leaf+host) : 1000 for leaf in range(1,leaves+1) for host in range(1,hosts_per_leaf+1)}

        return { "nodes": nodes, "links":links, "links_table":spine_to_leaf_links + leaf_to_hosts_links}


    def operate(self):
        template = self.prepare_template()
        for number, terminals in self.terminals_per_tree.items():
            traffic = self.predict_traffic(number)
            output = template.render(graph=self.graph, terminals=terminals)
            with open("/home/mpodles/iFabric/src/main/Controller/Network_Graph_from_template.sg",'w+')  as f:
                f.write(output)
            steiner_graph = self.get_steiner_graph()
            self.update_graph(traffic,steiner_graph)
            

    def prepare_template(self):
        file_loader = jinja2.FileSystemLoader(os.path.dirname(
            self.topology_template_path
        ))
        env = jinja2.Environment(loader=file_loader)

        template=env.get_template(os.path.basename(
            self.topology_template_path
        ))
        return template

    def get_steiner_graph(self):
        cmd = "/home/mpodles/iFabric/src/main/Controller/Steiner_Calculator < /home/mpodles/iFabric/src/main/Controller/Network_Graph_from_template.sg"
        result = subprocess.check_output(cmd, shell=True)
        return result
        return self.parse_result(result)
        
    def parse_result(self,result):
        edges = []
        for line in result:
            if not line.contains("VALUE"):
                edges.append(line.split(" "))
        return edges

    def predict_traffic(self, number):
        return random.randint(10,150)

    def update_graph(self, traffic,steiner_graph):
        for edge in steiner_graph:
            self.graph[links_table]


agent = iFabricMainframe("/home/mpodles/iFabric/src/main/configuration_files/Network_graph_template.jinja2",None)
agent.operate()
