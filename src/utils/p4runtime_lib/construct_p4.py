import json
import re

class P4Constructor():
    def __init__(self):
        self.project_directory = "/home/mpodles/Documents/iFabric/src/main/"
        self.ingress_tables = ["MyIngress.flow_classifier"]
        self.ingress_tables_actions = {"MyIngress.flow_classifier": "append_myTunnel_header"} 
        self.egress_tables = ["MyEgress.port_checker"]
        self.egress_tables_actions = {"MyEgress.port_checker": "strip_header"}
        self.connections = {}
        try:
            self.read_topology()
            self.parse_topology()
            self.read_flows()
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
        print self.links
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
            flows = json.load(f)
            self.flows = flows['flows']

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
        
    def construct_p4_program(self):
        protocols = self.flows.keys()
        self.fill_p4_template(protocols)

    def fill_p4_template(self, protocols):
        # TODO
        pass

    def construct_runtimes(self):
        for sw in self.switches:
            self.construct_switch_runtime_json(sw)
    

    def construct_switch_runtime_json(self, sw):
        ingress_tables_entries = self.generate_tables_entries(sw, pipeline= "ingress")

        egress_tables_entries = self.generate_tables_entries(sw, pipeline= "egress")

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
            
    def generate_tables_entries(self, sw , pipeline):
        tables_entries = []
        if pipeline == "ingress":
            tables=self.ingress_tables
        elif pipeline == "egress":
            tables=self.egress_tables
        for table in tables:
            for flow in self.flows:
                tables_entries.append(self.generate_table_entry(sw,flow,table))
        return tables_entries

    
    def generate_multicast_groups_entries(self, sw):
        used_ports = self.get_used_switch_ports(sw)
        multicast_group_entries = []
        for flow_id in self.ids:
            replicas = self.generate_replicas(used_ports)
            multicast_group = {"multicast_group_id" :flow_id, "replicas": replicas }
            multicast_group_entries.append(multicast_group)

    def get_used_switch_ports(self, sw):
        switchports,endports =  self.topology[sw]["switchports"],self.topology[sw]["endports"]
        ports = []
        for entry in switchports + endports:
            ports.append(entry["port"])
        return ports

    def generate_replicas(self, used_ports):
        #TODO: make the random_subset random
        random_subset = used_ports
        replicas = []
        for port in random_subset:
            replicas.append({"egress_port": port, "instance": port})
        return replicas

    def generate_table_entry(self, sw, flow, table):
        for match_key, match_value in self.flows[flow]:
            self.parse_flow
            table_entry = {
                    "table": table,
                    "match": {
                    match_key : match_value
                    },
                    "action_name": "MyIngress.append_myTunnel_header",
                    "action_params": {
                    "flow_id": self.ids["flow2"],
                    "node_id": self.ids["h2"],
                    "group_id": 1
                    }
                }
        return table_entry

    def parse_flow(self, sw, flow):
        pass

if __name__ == '__main__':
    constructor = P4Constructor()
    print constructor.flows["flow2"]
    print constructor.ids
    print constructor.topology
    for i in range (1,5):
        print constructor.get_used_switch_ports("s"+str(i))
    
