import json
import re
import random
import jinja2
import os


class TableEntry():
    switch=''
    flow = ''
    table_name=''
    match_field_name = ''
    match_value= {"low": '', "high":''}
    action = ''
    action_parameters = {}
    priority = None
    


class P4Constructor():
    def __init__(self):
        self.project_directory = "/home/mpodles/iFabric/src/main/"
        self.tables = ["Node_classifier"]
        self.match_field_name_table = {"standard_metadata.ingress_port": "Node_classifier"}
        self.tables_action = {"MyIngress.Node_classifier": "MyIngress.append_myTunnel_header", "MyEgress.port_checker": "MyIngress.strip_header"}
        self.actions_parameters = {"MyIngress.append_myTunnel_header": ["flow_id", "node_id", "group_id"], "MyIngress.fix_header":["flow_id", "priority"], "MyEgress.strip_header": [] }
        self.connections = {}

        self.read_topology()
        self.parse_topology()
        self.read_protocols_implemented_and_required()
        self.read_flows()
        self.parse_flows()
        self.prepare_nodes_flows()
        self.generate_tables_actions()
        self.generate_ids_for_flows()
        self.construct_p4_program()
        self.construct_runtimes()
        self.write_flow_ids_to_file()

       
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
            curr_priority = flow_values.pop("priority") * 100 #multiply by 100 to have higher priority spread
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
        self.match_field_name_table[match_field_name] = table_name
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

    def prepare_nodes_flows(self):
        self.switches_node_flows = {}
        for switch, ports in self.topology.items():
            self.switches_node_flows[switch] = {} 
            for port_dict in ports["endports"]:
                port, host = port_dict["port"],port_dict["host"]
                if self.switches_node_flows[switch].get(host+ "_flow") is not None:
                    self.switches_node_flows[switch][host+ "_flow"]["standard_metadata.ingress_port"].append({"low": port, "high": port})
                    self.flows[host+ "_flow"]["standard_metadata.ingress_port"].append({"low": port, "high": port})
                else:                
                    self.switches_node_flows[switch][host+ "_flow"] = {"standard_metadata.ingress_port": [{"low": port, "high": port}]}
                    self.flows[host+ "_flow"] = {"standard_metadata.ingress_port": [{"low": port, "high": port}]}

    def generate_tables_actions(self):
        for table_name in self.match_field_name_table.values():
            if table_name != "Node_classifier":
                self.tables_action["MyIngress." + table_name] = "MyIngress.fix_header"


    def generate_ids_for_flows(self):
        self.flow_ids = {}
        id = 0
        for flow in self.flows:
            id+=1
            self.flow_ids[flow] = id
        
    def construct_p4_program(self):
        self.fill_p4_template()

    def fill_p4_template(self):
        template_directory = self.project_directory + "sig-topo/"

        file_loader = jinja2.FileSystemLoader(template_directory)
        env = jinja2.Environment(loader=file_loader)
        template=env.get_template("fabric_tunnel_template.jinja2")

        output = template.render(match_field_name_table=self.match_field_name_table,\
             protocols=self.implemented_protocols, next_protocols_fields = self.next_protocols_fields)
        # with open(template_directory+"fabric_tunnel_ready.p4",'w+')  as f:
        #      f.write(output)
        with open(self.project_directory + "fabric_tunnel.p4",'w+')  as f:
             f.write(output)
        

    def construct_runtimes(self):
        for sw in self.switches:
            self.construct_runtime_for_switch(sw)
    

    def construct_runtime_for_switch(self, sw):
        tables_entries = self.generate_tables_entries_for_switch(sw)

        multicast_group_entries = self.generate_multicast_groups_entries(sw)

        tables_entries = self.turn_table_entries_into_dicts(tables_entries)

        result_dictionary = {
            "target": "bmv2",
            "p4info": "build/fabric_tunnel.p4.p4info.txt",
            "bmv2_json": "build/fabric_tunnel.json",
            "table_entries": tables_entries,
            "multicast_group_entries" : multicast_group_entries
        }

        result_string = json.dumps(result_dictionary, encoding='UTF-8')

        with open(self.project_directory + "sig-topo/" + sw + "-runtime.json", "w") as f:
            f.write(result_string)
            
    def generate_tables_entries_for_switch(self, sw):
        switch_tables_entries = []
        for (flow_name, priority) in self.flows_by_priority_with_priority:
                switch_tables_entries += self.generate_table_entries_for_flow_for_switch(sw, flow_name, priority)
        for flow_name in self.switches_node_flows[sw]:
                switch_tables_entries += self.generate_table_entries_for_flow_for_switch(sw, flow_name, 1)
        switch_tables_entries += self.generate_egress_table_entries(sw)
        return switch_tables_entries

    def generate_table_entries_for_flow_for_switch(self, sw, flow, priority):
        one_flow_switch_table_entries = []
        if priority >  0:
            rules = self.flows[flow]
        else:
            rules = self.switches_node_flows[sw][flow]
        for match_field_name, match_field_values in rules.items():
            table_name = "MyIngress." + self.match_field_name_table[match_field_name]
            action = self.tables_action[table_name]
            priority_offset = 0
            for values_range in match_field_values:
                table_entry = TableEntry()
                table_entry.switch = sw
                table_entry.flow = flow
                table_entry.table_name = table_name
                table_entry.match_field_name = match_field_name
                table_entry.match_value= {"low": values_range["low"], "high":values_range["high"]}
                table_entry.action = action
                table_entry.priority = priority
                table_entry = self.set_table_entry_action_parameters(table_entry)
                table_entry.priority = priority + priority_offset

                # action_parameters = self.get_action_params_for_current_flow(flow, priority)
                priority_offset += 1

                one_flow_switch_table_entries.append(table_entry)
        return one_flow_switch_table_entries

    def generate_egress_table_entries(self, sw):
        egress_entries = []
        priority = 1 
        table_name = "MyEgress.port_checker"
        action = "MyEgress.strip_header"
        host_ports = set([])
        for endport in self.topology[sw]["endports"]:
            host_ports.add(endport["port"])
        for port in host_ports:
            table_entry = TableEntry()
            table_entry.switch = sw
            table_entry.table_name = table_name
            table_entry.match_field_name = "standard_metadata.egress_port"
            table_entry.match_value= {"low": port, "high":port}
            table_entry.action = action
            table_entry.action_parameters = ''
            table_entry.priority = priority
            egress_entries.append(table_entry)

            priority += 1
        return egress_entries

    def set_table_entry_action_parameters(self, table_entry):
        action_parameters = self.actions_parameters[table_entry.action]
        filled_parameters = {}
        for parameter in action_parameters:
            if parameter == "flow_id":
                filled_parameters[parameter] = self.flow_ids[table_entry.flow]
            elif parameter == "priority": 
                filled_parameters[parameter] = table_entry.priority
            elif parameter == "node_id":
                filled_parameters[parameter] = self.flow_ids[table_entry.flow]
            elif parameter == "group_id":
                filled_parameters[parameter] = self.flow_ids[table_entry.flow] + 100

        table_entry.action_parameters = filled_parameters
        return table_entry

    def turn_table_entries_into_dicts(self, table_entries):
        result_table_entries = []
        for table_entry in table_entries:
            low = table_entry.match_value["low"]
            high = table_entry.match_value["high"]
            if self.represents_int(low):
                low = int(low)
            if self.represents_int(high):
                high = int(high)
            result_table_entry = {
            "table": table_entry.table_name,
            "priority": table_entry.priority,
            "match": {
                table_entry.match_field_name: [low, high]
            },
            "action_name": table_entry.action,
            "action_params": table_entry.action_parameters
            }

            # if table_entry.priority is not None:
            #     result_table_entry["priority"] = table_entry.priority
            result_table_entries.append(result_table_entry)
        return result_table_entries

    def generate_multicast_groups_entries(self, sw):
        used_ports = self.get_used_switch_ports(sw)
        multicast_group_entries = []
        for flow_id in self.flow_ids.values():
            replicas = self.generate_replicas(used_ports)
            multicast_group = {"multicast_group_id" :flow_id, "replicas": replicas }
            multicast_group_entries.append(multicast_group)
        return multicast_group_entries
    
    def represents_int(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False
    
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
            replicas.append({"egress_port": int(port), "instance": int(port)})
        return replicas

    def write_flow_ids_to_file(self):
        with open(self.project_directory+ "build/flow_ids.json", "w") as f:
            f.write(json.dumps(self.flow_ids))


if __name__ == '__main__':
    constructor = P4Constructor()
    print "P4 constructed"
    # constructor.generate_table_entry_for_flow("s1", "flow2", "MyIngress.flow_classifier")
    # print constructor.flows["flow2"]
    # print constructor.ids
    # #print constructor.topology
    # print constructor.flows
    # for a,b in  constructor.flows["flow2"].items():
    #     print a,b
    
