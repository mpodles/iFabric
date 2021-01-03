import json
import re
import random
import jinja2
import os


class TableEntry():
    switch=''
    table_name=''
    match_field_name = ''
    match_value= {"low": '', "high":''}
    action = ''
    action_parameters = {}
    priority = int
    


class P4Constructor():
    def __init__(self):
        self.project_directory = "/home/mpodles/iFabric/src/main/"
        self.tables = ["Node_classifier"]
        self.match_field_name_table = {"standard_metadata.ingress_port": "Node_classifier"}
        # # self.ingress_protocols_abbrev = {"standard_metadata.ingress_port": "Node"}
        # self.egress_tables = ["MyEgress.port_checker"]
        self.tables_action = {"MyIngress.Node_classifier": "append_myTunnel_header", "MyEgress.port_checker": "strip_header"}
        self.actions_parameters = {"append_myTunnel_header": ["flow_id", "node_id", "group_id"], "fix_header":["flow_id", "priority"], "strip_header": [] }
        self.connections = {}
        try:
            self.read_topology()
            self.parse_topology()
            self.read_protocols_implemented_and_required()
            self.read_flows()
            self.parse_flows()
            self.generate_tables_actions()
            #self.read_policy()
            self.generate_ids_for_flows()
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
            
    def read_protocols_implemented_and_required(self):
        protocols_dir = self.project_directory + "/protocols/"
        self.implemented_protocols = {}
        for filename in os.listdir(protocols_dir):
            with open(protocols_dir + filename) as f:
                self.implemented_protocols[filename] = f.read()
        
        protocols_stack_file = self.project_directory + "/sig-topo/protocol_stack.json"
        with open(protocols_stack_file, "r") as f:
            protocols_stack = json.loads(f.read())
            self.protocols_stack = protocols_stack["stacks"]
            self.next_protocols_fields = protocols_stack["next_prot_fields"]
        

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

    def generate_tables_actions(self):
        for (table_name,_) in self.tables_with_matching_field_name:
            if table_name != "Node_classifier":
                self.tables_action["MyIngress." + table_name] = "fix_header"
            

    def parse_flow(self, flow_values, priority):
        #parse flow into priority + rules where rules is dict of protcols and list of range dicts,
        #range dicts contain low and high 
        parsed_flow = {}
        for entry in flow_values.items():
            match_field_name, values = self.parse_match_field_entry(entry)
            parsed_flow[match_field_name] = values
        return parsed_flow

    def parse_match_field_entry(self,match_field_entry):
        match_field_name, match_field_values = match_field_entry
        match_field_name = self.parse_match_field_name(match_field_name)
        match_field_values = self.parse_match_field_values(match_field_values)
        return match_field_name, match_field_values


    def parse_match_field_name(self, match_field_name):
        #Dictionary for parsing user match_field name to usable p4 logic
        #For now we assume correct match_field naming provided in json
        #The function also fills dict containing table name for each match_field_name and list of all tables

        # match_field_name, table_name = self.protocol_abbrev(match_field_name)
        match_field_name, table_name = "hdr." + match_field_name, match_field_name.replace(".", "_") + "_classifier"
        self.table_for_match_field_name[match_field_name] = table_name
        self.tables.append(table_name)
        return match_field_name

    def protocol_abbrev(self, protocol_name):
        #TODO: add parsing any kind of protocol name like "tcp destination"
        if 'tcp' in protocol_name:
            return 'TCP'
        elif 'ethernet' in  protocol_name:
            return  'Ethernet'
        elif 'ipv4' in protocol_name:
            return 'IPv4'

    def parse_match_field_values(self, match_field_values):
        #Dictionary for parsing user match_field values
        #into usable p4 low high bounds, for now we assume correct
        #parsing or in case of single value we change into correct parsing
        if type(match_field_values) == unicode:
            match_field_values = [{"low": match_field_values, "high": match_field_values}]
        return match_field_values

    def read_policy(self):
        policy_file = self.project_directory + "sig-topo/policy.json"
        with open(policy_file, 'r') as f:
            self.policy = json.load(f)

    def generate_ids_for_flows(self):
        self.flow_ids = {}
        id = 0
        for flow in self.flows:
            id+=1
            self.flow_ids[flow] = id

        for host in self.hosts:
            id+=1
            self.flow_ids[host] = id
        
    def construct_p4_program(self):
        self.fill_p4_template()

    def fill_p4_template(self):
        template_directory = self.project_directory + "sig-topo/"

        file_loader = jinja2.FileSystemLoader(template_directory)
        env = jinja2.Environment(loader=file_loader)
        template=env.get_template("fabric_tunnel_template.jinja2")

        output = template.render(tables_with_matching_field_name=self.tables_with_matching_field_name,\
             protocols=self.implemented_protocols, next_protocols_fields = self.next_protocols_fields)
        with open(template_directory+"fabric_tunnel_ready.p4",'w+')  as f:
             f.write(output)
        with open(self.project_directory + "fabric_tunnel.p4",'w+')  as f:
             f.write(output)
        

    def construct_runtimes(self):
        for sw in self.switches:
            self.construct_runtime_for_switch(sw)
    

    def construct_runtime_for_switch(self, sw):
        tables_entries = self.generate_tables_entries_for_switch

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

        # with open("/home/mpodles/Documents/iFabric/src/main/sig-topo/" + sw + "-runtime.json", "w") as f:
        #     f.write(result_string)
            
    def generate_tables_entries_for_switch(self, sw):
        switch_tables_entries = []
        for (flow_name, priority) in self.flows_by_priority_with_priority:
                switch_tables_entries.append(self.generate_table_entry_for_flow_for_switch(sw,flow_name,priority))
        return switch_tables_entries

    def generate_table_entries_for_flow_for_switch(self, sw, flow, priority):
        one_flow_switch_table_entries =
        for flow,rules in self.flows.items():
            for match_field_name, match_field_values in rules:
                for values
                action_params = {}
                for param in self.actions_parameters[action]:
                    action_params[param] = self.get_param_value(sw, param,flow)
                
        return table_entries

    def generate_table_entry_for_flow_for_table_for_switch(self, sw, flow, priority, table):


    def get_param_value(self, sw, param, flow):
        if param == "flow_id":
            return self.flow_ids[flow]
        elif param == "node_id":
            return 404 + self.flow_ids[flow]
        elif param == "group_id": 
            return 405 + self.flow_ids[flow]
        

    def generate_multicast_groups_entries(self, sw):
        used_ports = self.get_used_switch_ports(sw)
        multicast_group_entries = []
        for flow_id in self.flow_ids:
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
    # constructor.generate_table_entry_for_flow("s1", "flow2", "MyIngress.flow_classifier")
    # print constructor.flows["flow2"]
    # print constructor.ids
    # #print constructor.topology
    # print constructor.flows
    # for a,b in  constructor.flows["flow2"].items():
    #     print a,b
    
