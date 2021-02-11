class FlowTelemetry(Telemetry):
    def __init__(self, **params):
        super(self, Telemetry).__init__()
        self.states = [SwitchFlowsState(**params)]
