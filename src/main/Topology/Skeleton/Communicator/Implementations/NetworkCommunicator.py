class NetworkCommunicator(Communicator):
    def __init__(self, states, actions):
        super(self, Communicator).__init__()
        self.states = [NetworkFlow(**params)]
        self.actions = []