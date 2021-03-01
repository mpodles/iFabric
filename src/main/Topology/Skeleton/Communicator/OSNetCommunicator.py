class OSNetCommunicator(object):
    def __init__(self, device, **params):
        self.device = device
        self.connections = {}
        self.OSN_States = {}
        self.OSN_Actions = {}

    def connect(self):
        pass    

    def disconnect(self):
        pass

    def get_state(self, state, **params):
        self.OSN_States[state](**params)

    def take_action(self, action, **params):
        self.OSN_Actions[action](**params)
