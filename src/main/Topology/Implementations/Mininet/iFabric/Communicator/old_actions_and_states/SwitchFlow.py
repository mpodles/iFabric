import State

class SwitchFlow(State):
    def __init__(self, switch_name, flow, p4info_helper, sw_conn, used_ports):
        State.__init__(self)
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

    def __call__(self):
        return self.state_data