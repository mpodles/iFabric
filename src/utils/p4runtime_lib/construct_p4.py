import json
import re
import random
import jinja2


class TableEntry():
    switch=''
    table_name=''
    match_values= []
    action = ''
    action_parameters = []
    


class P4Constructor():
    def __init__(self):
        self.project_directory = "/home/mpodles/Documents/iFabric/src/main/"
        self.ingress_tables = ["MyIngress.node_and_group_classifier", "MyIngress.flow_classifier"]
        self.ingress_protocols = set(["standard_metadata.ingress_port"])
        self.egress_tables = ["MyEgress.port_checker"]
        self.tables_action = {"MyIngress.flow_classifier": "append_myTunnel_header", "MyIngress.node_and_group_classifier": "fix_header", "MyEgress.port_checker": "strip_header"}
        self.actions_parameters = {"append_myTunnel_header": ["flow_id", "node_id", "group_id"], "fix_header":["flow_id"], "strip_header": [] }
        self.connections = {}
        try:
            self.read_topology()
            self.parse_topology()
            self.read_flows()
            self.parse_flows()
            self.read_policy()
            self.generate_ids()
            self.construct_p4_program()
            #self.construct_switch_runtime_json()
        except Exception as e:
            print e
       
    def read_topology(self):
        topo_file = self.project_directory + "sig-topo/topology.json"
        with open(topo_file, 'r') as f:
            topo = json.load(f)
            self.switches = topo['switches']
            self.groups = topo['groups']
            self.links = topo['links']
            self.hosts = topo['hosts']

    def parse_topology(self):
        self.topology = self.prepare_skeleton()
        for link in self.links:
            self.parse_link(link)
                
    def prepare_skeleton(self):
        skeleton = {}
        for switch in self.switches:
            skeleton[switch] = {"switchports" : [], "endports": []}
        return skeleton

    def parse_link(self,link):
        if "h" in link[0]:
            host = link[0]
            switch_port = link[1]
            switch, port = re.match("(.+)-p([0-9]+)", switch_port).groups()
            entry = {"port":port, "host": host}
            self.topology[switch]["endports"].append(entry)
        elif "h" in link[1]:
            host = link[1]
            switch_port = link[0]
            switch, port = re.match("(.+)-p([0-9]+)", switch_port).groups()
            entry = {"port":port, "host": host}
            self.topology[switch]["endports"].append(entry)
        else:
            switch1, port1 = re.match("(.+)-p([0-9]+)", link[0]).groups()
            switch2, port2 = re.match("(.+)-p([0-9]+)", link[1]).groups()
            entry1 = {"port":port1,"connected_switch":switch2, "connected_port":port2}
            entry2 = {"port":port2,"connected_switch":switch1, "connected_port":port1}
            self.topology[switch1]["switchports"].append(entry1)
            self.topology[switch2]["switchports"].append(entry2)
            
        

    def read_flows(self):
        flows_file = self.project_directory + "sig-topo/flows.json"
        with open(flows_file, 'r') as f:
            self.flows = json.load(f)

    def parse_flows(self):
        #get priority list, pop priorities from dicts, parse match keys and values to proper p4
        self.flows_by_priority_with_priority = []
        priorities = []
        for flow_name, flow_values in self.flows.items():
            curr_priority = flow_values.pop("priority")
            index = 0
            for prio in priorities:
                if curr_priority > prio:
                    break
                index+=1
            priorities.insert(index, curr_priority)
            self.flows_by_priority_with_priority.insert(index, (flow_name, curr_priority))
            parsed_flow = self.parse_flow(flow_values, curr_priority)
            self.flows[flow_name] =  parsed_flow


    def parse_flow(self, flow_values, priority):
        #parse flow into priority + rules where rules is dict of protcols and list of range dicts,
        #range dicts contain low and high 
        parsed_flow = {}
        for entry in flow_values.items():
            protocol, values = self.parse_protocol_entry(entry)
            parsed_flow[protocol] = values
        return {"priority": priority, "rules": parsed_flow}

    def parse_protocol_entry(self,protocol_entry):
        protocol_name, protocol_values = protocol_entry
        protocol_name = self.parse_protocol_name(protocol_name)
        protocol_values = self.parse_protocol_values(protocol_values)
        return protocol_name, protocol_values


    def parse_protocol_name(self, protocol_name):
        #Dictionary for parsing user protocol name to usable p4 logic
        #For now we assume correct protocol naming provided in json
        self.ingress_protocols.add(protocol_name)
        return protocol_name

    def parse_protocol_values(self, protocol_values):
        #Dictionary for parsing user protocol name to usable p4 logic
        #For now we assume correct protocol naming provided in json
        print(type(protocol_values))
        if type(protocol_values) == unicode:
            protocol_values = [{"low": protocol_values, "high": protocol_values}]
        return protocol_values

    def read_policy(self):
        policy_file = self.project_directory + "sig-topo/policy.json"
        with open(policy_file, 'r') as f:
            self.policy = json.load(f)

    def generate_ids(self):
        self.ids = {}
        id = 0
        for flow in self.flows:
            id+=1
            self.ids[flow] = id

        for host in self.hosts:
            id+=1
            self.ids[host] = id

        for group in self.groups:
            id+=1
            self.ids[group] = id
        
    def construct_p4_program(self):
        self.fill_p4_template()

    def fill_p4_template(self):
        template_file = self.project_directory +"sig-topo/fabric_tunnel_template.jinja2"
        with open(template_file, 'r') as t:
            template = jinja2.Template(t.read())

    def construct_runtimes(self):
        for sw in self.switches:
            self.construct_switch_runtime_json(sw)
    

    def construct_switch_runtime_json(self, sw):
        ingress_tables_entries = self.generate_tables_entries_per_flow(sw, pipeline= "ingress")

        egress_tables_entries = self.generate_tables_entries_per_flow(sw, pipeline= "egress")

        tables_entries = ingress_tables_entries + egress_tables_entries

        multicast_group_entries = self.generate_multicast_groups_entries(sw)

        result_dictionary = \
        {
            "target": "bmv2",
            "p4info": "build/fabric_tunnel.p4.p4info.txt",
            "bmv2_json": "build/fabric_tunnel.json",
            "table_entries": tables_entries,
            "multicast_group_entries" : multicast_group_entries
        }

        result_string = json.dumps(result_dictionary)

        with open("/home/mpodles/Documents/iFabric/src/main/sig-topo/" + sw + "-runtime.json", "w") as f:
            f.write(result_string)
            
    def generate_tables_entries_per_flow(self, sw , pipeline):
        tables_entries = []
        if pipeline == "ingress":
            tables=self.ingress_tables
        elif pipeline == "egress":
            tables=self.egress_tables
        for table in tables:
            for flow in self.flows_by_priority_with_priority:
                tables_entries.append(self.generate_table_entry_for_flow(sw,flow,table))
        return tables_entries

    def generate_table_entry_for_flow(self, sw, flow, table):
        flow_name , priority = flow 
        for match_key, match_value in self.flows[flow].items():
            action = self.tables_action[table]
            action_params = {}
            for param in self.actions_parameters[action]:
                action_params[param] = self.get_param_value(sw, param,flow)
            table_entry = {
                    "table": table,
                    "priority": priority,
                    "match": {
                    match_key : match_value
                    },
                    "action_name": action,
                    "action_params": action_params
                }
        return table_entry    

    def get_param_value(self, sw, param, flow):
        if param == "flow_id":
            return self.ids[flow]
        elif param == "node_id":
            return 404 + self.ids[flow]
        elif param == "group_id": 
            return 405 + self.ids[flow]
        

    def generate_multicast_groups_entries(self, sw):
        used_ports = self.get_used_switch_ports(sw)
        multicast_group_entries = []
        for flow_id in self.ids:
            replicas = self.generate_replicas(used_ports)
            multicast_group = {"multicast_group_id" :flow_id, "replicas": replicas }
            multicast_group_entries.append(multicast_group)

    
    def get_used_switch_to_switch_ports(self,sw):
        switchports =  self.topology[sw]["switchports"]
        ports = []
        for entry in switchports:
            ports.append(entry["port"])
        return ports

    def get_used_switch_to_host_ports(self,sw):
        endports =  self.topology[sw]["endports"]
        ports = []
        for entry in endports:
            ports.append(entry["port"])
        return ports

    def get_used_switch_ports(self, sw):
        switchports,endports =  self.get_used_switch_to_switch_ports(sw),self.get_used_switch_to_host_ports(sw)
        ports = switchports + endports
        return ports

    def generate_replicas(self, used_ports):
        random_subset = []
        for port in used_ports:
            if random.randint(0,1) == 0:
                random_subset.append(port)
        replicas = []
        for port in random_subset:
            replicas.append({"egress_port": port, "instance": port})
        return replicas


if __name__ == '__main__':
    constructor = P4Constructor()
    constructor.generate_table_entry_for_flow("s1", "flow2", "MyIngress.flow_classifier")
    print constructor.flows["flow2"]
    print constructor.ids
    #print constructor.topology
    print constructor.flows
    for a,b in  constructor.flows["flow2"].items():
        print a,b
    
