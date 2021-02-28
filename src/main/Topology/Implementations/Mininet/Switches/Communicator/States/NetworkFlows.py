class NetworkFlows(State):
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