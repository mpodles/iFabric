import json 
import random 

#TODO: think on how to generalize this to the most useful case

class FlowGenerator():

    def __init__(self, **files):
        self.topology_file_path = files["topology_file_path"]
        self.flows_file_target_path = files["flows_file_target_path"]
        self.read_topology(self.topology_file_path)

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
        self.macs = []
        self.ips = []
        self.get_all_ips_and_macs()
        self.flows = {}
        self.prepare_flows()
        self.write_flows(self.flows_file_target_path)

    def get_all_ips_and_macs(self):
        for params in self.nodes.values(): 
            for interface, int_config in params.items():
                if interface != "commands":  #TODO: Change this so commands are not there 
                    self.macs.append(int_config["mac"])
                    self.ips.append(int_config["ip"])

    def prepare_flows(self):
        iterator = 0
        for mac in self.macs:
            iterator +=1
            self.flows["flow"+str(iterator)] = {
            "Ethernet.dstAddr": [mac],
            "priority": iterator
        }

        for ip in self.ips:
            iterator +=1
            self.flows["flow" + str(iterator)] = {
            "IPv4.dstAddr": [ip],
            "priority": iterator
        }

    def write_flows(self, flows_file_target_path):
        with open(flows_file_target_path, "w") as f:
            f.write(json.dumps(self.flows))
    