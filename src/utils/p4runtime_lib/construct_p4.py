import json

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
        self.match_links_to_nodes()


    def match_links_to_nodes(self):
        self.nodes_ports = [[node,port] for [node, port] in self.links if 'h' in node]

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

        tables_entries = ingress_tables_entries + egress_table_entries

        multicast_group_entries = self.generate_multicast_groups_entries(sw)

        result_dictionary = \
        {
            "target": "bmv2",
            "p4info": "build/fabric_tunnel.p4.p4info.txt",
            "bmv2_json": "build/fabric_tunnel.json",
            "table_entries": table_entries,
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

        multicast_group_entries= [
        {
        "multicast_group_id" : 1,
        "replicas" : [
          {
            "egress_port" : 48,
            "instance" : 1
          },
          {
            "egress_port" : 5,
            "instance" : 1
          }
        ]
        }
        ]
        for flow_id in self.ids:
            replicas = self.generate_replicas

            multicast_group = {"multicast_group_id" :flow_id }

            multicast_group_entries.append

    def get_used_switch_ports(self, sw):
        # TODO
        pass

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
    print constructor.nodes_ports
    print constructor.flows["flow2"]
    print constructor.ids
    
