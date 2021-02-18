import json
import re
import random
import jinja2
import os



class P4Constructor():
    def __init__(self, **files):
        protocols_folder_path = files["protocols_folder_path"] 
        protocols_required_file_path = files["protocols_required_file_path"] 
        template_file_path = files["template_file_path"] 
        p4_file_target_path = files["p4_file_target_path"]

        self.protocols = {}

        # self.match_fields_of_table = {"Flow_classifier": set(["standard_metadata.ingress_port"])}
        # self.tables_action = {"MyIngress.Flow_classifier": "MyIngress.append_myTunnel_header", "MyEgress.port_checker": "MyIngress.strip_header"}
        # self.actions_parameters = {"MyIngress.append_myTunnel_header": ["flow_id", "node_id", "group_id"], "MyEgress.strip_header": [] }

        self.read_protocols(protocols_folder_path, protocols_required_file_path)
        self.construct_p4_program(template_file_path, p4_file_target_path)
       

            
    def read_protocols(self, protocols_folder_path, protocols_required_file_path):
        with open(protocols_required_file_path, "r") as f:
            protocols_file = json.loads(f.read())
            self.protocols_used = protocols_file["protocols_used"]
            self.protocols_stack = protocols_file["stacks"]
            self.next_protocols_fields = protocols_file["next_prot_fields"]
            self.match_fields_used = protocols_file["match_fields_used"]
            self.fields_to_learn = protocols_file["fields_to_learn"] 
        
        for filename in os.listdir(protocols_folder_path):
            if filename in self.protocols_used:
                with open(os.path.join(protocols_folder_path, filename)) as f:
                    self.protocols[filename] = f.read()

    def construct_p4_program(self, template_file_path, p4_target_file_path):
        file_loader = jinja2.FileSystemLoader(os.path.dirname(template_file_path))
        env = jinja2.Environment(loader=file_loader)

        template=env.get_template(os.path.basename(template_file_path))
        output = template.render(match_fields_used=self.match_fields_used,\
                protocols=self.protocols, next_protocols_fields = self.next_protocols_fields)

        with open(p4_target_file_path,'w+')  as f:
             f.write(output)

    # def read_flows(self, flows_file_path):
    #     with open(flows_file_path, 'r') as f:
    #         self.flows = json.load(f)

    # def parse_flows(self):
    #     #get priority list, pop priorities from dicts, parse match keys and values to proper p4
    #     self.flows_by_priority_with_priority = []
    #     priorities = []
    #     for flow_name, flow_values in self.flows.items():
    #         curr_priority = flow_values.pop("priority") * 100 #multiply by 100 to have higher priority spread
    #         index = 0
    #         for prio in priorities:
    #             if curr_priority > prio:
    #                 break
    #             index+=1
    #         priorities.insert(index, curr_priority)
    #         self.flows_by_priority_with_priority.insert(index, (flow_name, curr_priority))
    #         parsed_flow = self.parse_flow(flow_values, curr_priority)
    #         self.flows[flow_name] =  parsed_flow
            

    # def parse_flow(self, flow_values, priority):
    #     #parse each entry (usually that means a protocol field) of flow
    #     parsed_flow = {}
    #     for entry in flow_values.items():
    #         match_field_name, values = self.parse_match_field_entry(entry)
    #         parsed_flow[match_field_name] = values
    #     return parsed_flow

    # def parse_match_field_entry(self,match_field_entry):
    #     match_field_name, match_field_values = match_field_entry
    #     match_field_name = self.parse_match_field_name(match_field_name)
    #     match_field_values = self.parse_match_field_values(match_field_values)
    #     return match_field_name, match_field_values


    # def parse_match_field_name(self, match_field_name):
    #     #Dictionary for parsing user match_field name to usable p4 logic
    #     #For now we assume correct match_field naming provided in json
    #     #The function also fills dict containing table name for each match_field_name and list of all tables

    #     # match_field_name, table_name = self.protocol_abbrev(match_field_name)

    #     match_field_name, table_name = "hdr." + match_field_name, "Flow_classifier"
    #     if self.match_fields_of_table.get(table_name) is not None:
    #         self.match_fields_of_table[table_name].add(match_field_name)
    #     else:
    #         self.match_fields_of_table[table_name] = set([])
    #     return match_field_name

    # def protocol_abbrev(self, protocol_name):
    #     #TODO: add parsing any kind of protocol name like "tcp destination"
    #     if 'tcp' in protocol_name:
    #         return 'TCP'
    #     elif 'ethernet' in  protocol_name:
    #         return  'Ethernet'
    #     elif 'ipv4' in protocol_name:
    #         return 'IPv4'

    # def parse_match_field_values(self, match_field_values):
    #     #Dictionary for parsing user match_field values
    #     #into usable p4 low high bounds, for now we assume correct
    #     #parsing or in case of single value we change into correct parsing
    #     parsed_match_field_values = []
    #     for match_entry in match_field_values:
    #         if type(match_entry) != dict:
    #             if self.represents_int(match_entry):
    #                 match_entry = int(match_entry)
    #             parsed_match_field_values.append({"low": match_entry, "high": match_entry})
    #         else:
    #             low = match_entry["low"]
    #             high = match_entry["high"]
    #             if self.represents_int(low):
    #                 low = int(low)
    #             if self.represents_int(high):
    #                 high = int(high) 
    #             parsed_match_field_values.append({"low": low, "high": high})
    #     return parsed_match_field_values

    # def prepare_nodes_flows(self):
    #     self.switches_node_flows = {}
    #     for switch, ports in self.topology.items():
    #         self.switches_node_flows[switch] = {} 
    #         for port_dict in ports["endports"]:
    #             port, host = int(port_dict["port"]),port_dict["node"]
    #             if self.switches_node_flows[switch].get(host+ "_flow") is not None:
    #                 self.switches_node_flows[switch][host+ "_flow"]["standard_metadata.ingress_port"].append({"low": port, "high": port})
    #                 self.flows[host+ "_flow"]["standard_metadata.ingress_port"].append({"low": port, "high": port})
    #             else:                
    #                 self.switches_node_flows[switch][host+ "_flow"] = {"standard_metadata.ingress_port": [{"low": port, "high": port}]}
    #                 self.flows[host+ "_flow"] = {"standard_metadata.ingress_port": [{"low": port, "high": port}]}

    # def generate_ids_for_flows(self):
    #     self.flows_ids = {}
    #     id = 0
    #     for flow in self.flows:
    #         id+=1
    #         self.flows_ids[flow] = id
        
    # def construct_p4_program(self, template_file_path, p4_target_file_path):
    #     file_loader = jinja2.FileSystemLoader(os.path.dirname(template_file_path))
    #     env = jinja2.Environment(loader=file_loader)

    #     template=env.get_template(os.path.basename(template_file_path))
    #     output = template.render(match_fields_of_table=self.match_fields_of_table,\
    #             protocols=self.implemented_protocols, next_protocols_fields = self.next_protocols_fields)

    #     with open(p4_target_file_path,'w+')  as f:
    #          f.write(output)
        
    # def construct_runtimes(self, compiled_p4_target_file_path, p4runtime_target_file_path):
    #     self.runtimes = {}
    #     for sw in self.switches:
    #         self.runtimes[sw] = self.construct_runtime_for_switch(sw, compiled_p4_target_file_path, p4runtime_target_file_path)
    
    # def construct_runtime_for_switch(self, sw, compiled_p4_target_file_path, p4runtime_target_file_path):
    #     tables_entries = self.generate_tables_entries_for_switch(sw)

    #     multicast_group_entries = self.generate_multicast_groups_entries(sw)

    #     tables_entries = self.turn_table_entries_into_dicts(tables_entries)

    #     result_dictionary = {
    #         "target": "bmv2",
    #         "p4info": p4runtime_target_file_path,
    #         "bmv2_json": compiled_p4_target_file_path,
    #         "table_entries": tables_entries,
    #         "multicast_group_entries" : multicast_group_entries
    #     }

    #     return json.dumps(result_dictionary, encoding='UTF-8') #UTF-8 probably not required

    # def generate_tables_entries_for_switch(self, sw):
    #     switch_tables_entries = []
    #     for (flow_name, priority) in self.flows_by_priority_with_priority:
    #             switch_tables_entries += self.generate_table_entries_for_flow_for_switch(sw, flow_name, priority)
    #     priority = 0
    #     for flow_name in self.switches_node_flows[sw]:
    #             priority+=1
    #             switch_tables_entries += self.generate_table_entries_for_flow_for_switch(sw, flow_name, priority)
    #     switch_tables_entries += self.generate_egress_table_entries(sw)
    #     return switch_tables_entries

    # def generate_table_entries_for_flow_for_switch(self, sw, flow, priority):
    #     one_flow_switch_table_entries = []
    #     flow_matches = self.flows[flow]
    #     for table_name in self.tables:
    #         table_name = "MyIngress." + table_name
    #         match_fields_size= {}
    #         all_combinations = 1
    #         for match_field_name, match_field_values in flow_matches.items():
    #             size = len(match_field_values)
    #             match_fields_size[match_field_name] = size
    #             all_combinations *= size
    #         compound_iterator = 0

    #         while compound_iterator < all_combinations:
    #             matches = {}
    #             match_iterator = compound_iterator
    #             for match_field_name, match_field_size in match_fields_size.items():
    #                 matches[match_field_name] = flow_matches[match_field_name][match_iterator % match_field_size]
    #                 match_iterator /= match_field_size
                    

    #             action = self.tables_action[table_name]
    #             table_entry = TableEntry()
    #             table_entry.switch = sw
    #             table_entry.flow = flow
    #             table_entry.table_name = table_name
    #             table_entry.matches = matches
    #             table_entry.action = action
    #             table_entry.priority = priority
    #             table_entry = self.set_table_entry_action_parameters(table_entry)
    #             table_entry.priority = priority + compound_iterator
    #             compound_iterator +=1 
    #             # action_parameters = self.get_action_params_for_current_flow(flow, priority)

    #             one_flow_switch_table_entries.append(table_entry)
    #     return one_flow_switch_table_entries


    # def generate_egress_table_entries(self, sw):
    #     egress_entries = []
    #     priority = 1 
    #     table_name = "MyEgress.port_checker"
    #     action = "MyEgress.strip_header"
    #     host_ports = set([])
    #     for endport in self.topology[sw]["endports"]:
    #         host_ports.add(endport["port"])
    #     for port in host_ports:
    #         table_entry = TableEntry()
    #         table_entry.switch = sw
    #         table_entry.table_name = table_name
    #         table_entry.matches = {"standard_metadata.egress_port": {"low": int(port), "high": int(port) }}
    #         table_entry.action = action
    #         table_entry.action_parameters = ''
    #         table_entry.priority = priority
    #         egress_entries.append(table_entry)

    #         priority += 1
    #     return egress_entries

    # def set_table_entry_action_parameters(self, table_entry):
    #     action_parameters = self.actions_parameters[table_entry.action]
    #     filled_parameters = {}
    #     for parameter in action_parameters:
    #         if parameter == "flow_id":
    #             filled_parameters[parameter] = self.flows_ids[table_entry.flow]
    #         elif parameter == "priority": 
    #             filled_parameters[parameter] = table_entry.priority
    #         elif parameter == "node_id":
    #             filled_parameters[parameter] = self.flows_ids[table_entry.flow]
    #         elif parameter == "group_id":
    #             filled_parameters[parameter] = self.flows_ids[table_entry.flow] + 100

    #     table_entry.action_parameters = filled_parameters
    #     return table_entry

    # def turn_table_entries_into_dicts(self, table_entries):
    #     result_table_entries = []
    #     for table_entry in table_entries:
    #         result_table_entry = {
    #         "table": table_entry.table_name,
    #         "priority": table_entry.priority,
    #         "match": table_entry.matches,
    #         "action_name": table_entry.action,
    #         "action_params": table_entry.action_parameters
    #         }
    #         result_table_entries.append(result_table_entry)
    #     return result_table_entries

    # def represents_int(self, string):
    #     try:
    #         int(string)
    #         return True
    #     except ValueError:
    #         return False

    # def generate_multicast_groups_entries(self, sw):
    #     multicast_group_entries = []
    #     for flow_id in self.flows_ids.values():
    #         if self.multicast_begin_state == "empty":
    #             replicas = self.generate_replicas_empty()
    #         elif self.multicast_begin_state == "random":
    #             replicas = self.generate_replicas_random_rules(sw)
    #         multicast_group = {"multicast_group_id" :flow_id, "replicas": replicas }
    #         multicast_group_entries.append(multicast_group)
    #     return multicast_group_entries
    
    # def generate_replicas_empty(self):
    #     replicas = []
    #     return replicas

    # def generate_replicas_random_rules(self, sw):
    #     used_ports = self.get_used_switch_ports(sw)
    #     random_subset = []
    #     for port in used_ports:
    #         if random.randint(0,1) == 0:
    #             random_subset.append(port)
    #     replicas = []
    #     for port in random_subset:
    #         replicas.append({"egress_port": int(port), "instance": int(port)})
    #     return replicas

    # def get_used_switch_ports(self, sw):
    #     switchports,endports =  self.get_used_switch_to_switch_ports(sw),self.get_used_switch_to_host_ports(sw)
    #     ports = switchports + endports
    #     return ports

    # def get_used_switch_to_switch_ports(self,sw):
    #     switchports =  self.topology[sw]["switchports"]
    #     ports = []
    #     for entry in switchports:
    #         ports.append(entry["port"])
    #     return ports

    # def get_used_switch_to_host_ports(self,sw):
    #     endports =  self.topology[sw]["endports"]
    #     ports = []
    #     for entry in endports:
    #         ports.append(entry["port"])
    #     return ports

    # def write_runtimes(self, runtimes_files_path):
    #     for sw, runtime in self.runtimes.items():
    #         with open(os.path.join(runtimes_files_path, sw + "-runtime.json"), "w") as f:
    #             f.write(runtime)

    # def write_flow_ids_to_file(self, flows_ids_file_path):
    #     with open(flows_ids_file_path, "w") as f:
    #         f.write(json.dumps(self.flows_ids))

