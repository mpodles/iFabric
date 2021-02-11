import concurrent.futures
import subprocess
import os
import jinja2
import random
import timeit
import copy
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
        self.links_bandwidth = 1e9
        

    def initialize_operation(self):
        self.terminals_per_tree = self.prepare_policy_trees()
        self.graph = self.get_topology_graph()


    def prepare_policy_trees(self):
        terminal_nodes = {}
        for i in range (100):
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
        {(leaf+spines, leaves+spines +(leaf-1)*hosts_per_leaf+host) : 100000 for leaf in range(1,leaves+1) for host in range(1,hosts_per_leaf+1)}

        return { "nodes": nodes, "links":links, "links_table":dict(spine_to_leaf_links, **leaf_to_hosts_links)}


    def operate(self):
        template = self.prepare_template()
        start = timeit.default_timer()
        for number, terminals in self.terminals_per_tree.items():
            traffic = self.predict_traffic(number)
            filled_graph = self.get_filled_graph(traffic)
            with open("/home/mpodles/iFabric/src/main/Controller/Network_Graph_from_template.sg",'w+')  as f:
                output = template.render(graph=filled_graph, terminals=terminals)
                f.write(output)

            steiner_graph = self.get_steiner_graph()
            self.fix_graph(steiner_graph, filled_graph)
        end = timeit.default_timer()
        print end-start
            

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
        return self.parse_result(result)
        
    def parse_result(self,result):
        edges = []
        for line in result.split("\n"):
            if "VALUE" not in line and line != '':
                node1,node2 =line.split(" ")
                node1,node2=int(node1),int(node2)
                if node1<node2:
                    edges.append((int(node1), int(node2)))
                else:
                    edges.append((int(node2), int(node1)))
        return edges

    def predict_traffic(self, number):
        return random.randint(1e6,0.5*1e8)

    def get_filled_graph(self, traffic):
        new_graph = copy.deepcopy(self.graph)
        for link, cost in new_graph["links_table"].items():
            new_graph["links_table"][link] = self.calculate_new_cost(cost,traffic)
        return new_graph

    
    def calculate_new_cost(self,cost,traffic):
        if cost >= 100000:
            return cost 
        else:
            saturation = self.cost_to_staturation(cost)
            new_saturation = saturation + traffic/self.links_bandwidth
            if new_saturation >1:
                return 100000
            return self.saturation_to_cost(new_saturation)
        
    
    def cost_to_staturation(self, cost):
        if cost<100:
            return 8.0*cost/1000.0
        else:
            return 7.0/9.0 + 2.0*cost/9000.0

    def saturation_to_cost(self,saturation):
        if saturation < 0.8:
            return int(12500 * saturation)
        else:
            return int(450000 * saturation - 350000)

    def fix_graph(self,steiner_graph, filled_graph):
        for edge in steiner_graph:
            self.graph["links_table"][edge]=filled_graph["links_table"][edge]


agent = iFabricMainframe("/home/mpodles/iFabric/src/main/configuration_files/Network_graph_template.jinja2",None)
agent.operate()