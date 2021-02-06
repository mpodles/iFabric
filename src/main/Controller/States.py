class State():
    def __init__(self):
        self.state_name = None
        self.state_data = None

    def get_state_data(self):
        pass

class SwitchFlowState(State):
    def __init__(self, switch_name, flow, p4info_helper, sw_conn, used_ports):
        super(self, State).__init__()
        self.switch_name = switch_name
        self.p4info_helper = p4info_helper
        self.flow_name, self.flow_id = flow
        self.sw_conn = sw_conn
        self.used_ports = used_ports
        self.p4info_ingress_counter = p4info_helper.get_counters_id("MyIngress.ingress_byte_cnt")
        self.p4info_egress_counter = p4info_helper.get_counters_id("MyIngress.egress_byte_cnt")
        
    def get_state_data(self):
        self.state_data = {}
        for port in self.used_ports:
            self.state_data[port] = {
                "ingress": self.get_ingress_port_bytes(port) , 
                "egress": self.get_egress_port_bytes(port)
                }
        return self.state_data

    def get_ingress_port_bytes(self, port):
        index = port + (self.flow_id-1)*48
        for response in self.sw_conn.ReadCounters( self.p4info_ingress_counter, int(index)):
            for entity in response.entities:
                counter = entity.counter_entry
                return counter.data.byte_count

    def get_egress_port_bytes(self, port):
        index = port + (self.flow_id-1)*48
        for response in self.sw_conn.ReadCounters(self.p4info_egress_counter, int(index)):
            for entity in response.entities:
                counter = entity.counter_entry
                return counter.data.byte_count  

class SwitchFlowsState(State):
    def __init__(self, switch_name, flows, p4info_helper, sw_conn, used_ports):
        super(self, State).__init__()
        self.p4info_helper = p4info_helper
        self.switch_name = switch_name
        self.flows = flows
        self.flow_states = {}
        self.sw_conn = sw_conn
        self.used_ports = used_ports

    def generate_flow_states(self):
        for flow_name, flow_id in self.flows.items():
            self.flow_states[flow_name] = SwitchFlowState(
                switch_name = self.switch_name,
                flow = (flow_name, flow_id),
                p4info_helper = self.p4info_helper,
                sw_conn = self.sw_conn,
                used_ports = self.used_ports
            )

    def get_state_data(self):
        self.state_data = {}
        for flow_name in self.flow_states.keys():
            self.state_data[flow_name] = self.flow_states[flow_name].get_state_data()
        return self.state_data

class NetworkFlowState(State):
    def __init__(self, topology, flow):
        super(self, State).__init__()
        self.flow_name, self.flow_id = flow
        self.topology = topology

        
    def get_state_data(self):
        self.state_data = {}
        for switch_name in self.topology: #TODO: look at topology structure
            p4info_helper, sw_conn, used_ports = switch_name["p4info_helper"], switch_name["sw_conn"], switch_name["used_ports"]
            p4info_ingress_counter = p4info_helper.get_counters_id("MyIngress.ingress_byte_cnt")
            p4info_egress_counter = p4info_helper.get_counters_id("MyIngress.egress_byte_cnt")
            for port in used_ports:
                self.state_data[port] = {
                "ingress": self.get_ingress_port_bytes(port, p4info_ingress_counter, sw_conn), 
                "egress": self.get_egress_port_bytes(port, p4info_egress_counter, sw_conn)
                }
        return self.state_data

    def get_ingress_port_bytes(self, port, p4info_ingress_counter, sw_conn):
        index = port + (self.flow_id-1)*48
        for response in sw_conn.ReadCounters(p4info_ingress_counter, int(index)):
            for entity in response.entities:
                counter = entity.counter_entry
                return counter.data.byte_count

    def get_egress_port_bytes(self, port, p4info_egress_counter, sw_conn):
        index = port + (self.flow_id-1)*48
        for response in sw_conn.ReadCounters(p4info_egress_counter, int(index)):
            for entity in response.entities:
                counter = entity.counter_entry
                return counter.data.byte_count  

class NetworkFlowsState(State):
    def __init__(self, topology, flows):
        super(self, State).__init__()
        self.topology = topology
        self.flows = flows
        self.flow_states = {}


    def generate_flow_states(self):
        for flow_name, flow_id in self.flows.items():
            self.flow_states[flow_name] = NetworkFlowState(
                topology = self.topology,
                flow = (flow_name, flow_id)
            )

    def get_state_data(self):
        self.state_data = {}
        for flow_name in self.flow_states.keys():
            self.state_data[flow_name] = self.flow_states[flow_name].get_state_data()
        return self.state_data
