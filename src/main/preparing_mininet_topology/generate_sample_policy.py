import json 
import random 

#TODO: think on how to generalize this to the most useful case

class PolicyGenerator():

    def __init__(self, **files):
        self.topology_file_path = files["topology_file_path"]
        self.flows_file_path = files["flows_file_path"]
        self.policy_file_target_path = files["policy_file_target_path"]
        self.read_topology(self.topology_file_path)
        self.read_flows(self.flows_file_path)


    def read_topology(self, topology_file_path):
        with open(topology_file_path, 'r') as f:
            topo = json.load(f)
            self.switches = topo['switches']
            self.groups = topo['groups']
            self.nodes = topo['nodes']
            self.topology = topo['links']
            self.nodes_links = topo['node_links']
        
    def read_flows(self, flows_file_path):
        with open(flows_file_path, 'r') as f:
            self.flows = json.load(f)
            



class DestinationPolicyGenerator(PolicyGenerator):

    def __init__(self, **files):
        PolicyGenerator.__init__(self, **files)
        self.policy = []
        self.prepare_policy()
        self.write_policy(self.policy_file_target_path)


    def prepare_policy(self):
        for flow_name, flow_fields in self.flows.items():
            for field_name, field_values in flow_fields.items():
                if field_name != "priority":
                    for value in field_values:
                        for node, properties in self.nodes.items():
                            for int_name, properties in properties.items():
                                if int_name != "commands" and (properties["mac"]==value or properties["ip"]==value):
                                    self.policy.append({"source":flow_name, "destination":node+"_"+int_name})
                            
    def write_policy(self, policy_file_target_path):
        with open(policy_file_target_path, "w") as f:
            f.write(json.dumps(self.policy))
    