class SwitchFlows(State):
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

