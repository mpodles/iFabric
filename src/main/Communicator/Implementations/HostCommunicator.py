class HostCommunicator(Communicator):
    def __init__(self, **params):
        super(self, Communicator).__init__()
        self.states = [NetworkFlowsState(**params)]