from States import SwitchFlowsState

class Telemetry():
    def __init__(self):
        self.states = {}
    
    def get_state(self, state, **params):
        self.states[state].get_state_data(**params)


class FlowTelemetry(Telemetry):
    def __init__(self, **params):
        super(self, Telemetry).__init__()
        self.states = {"flow_state_for_switch":SwitchFlowsState(**params)}


    
    
