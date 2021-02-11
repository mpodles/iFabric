class NetworkFlow(State):
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