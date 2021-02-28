class OSNetCommunicator(object):
    def __init__(self):
        self.connections = {}
        self.OSN_States = []
        self.OSN_Actions = []


    def connect(self, connection):
        connection.connect()

    def disconnect(self, connection):
        connection.disconnect()
            
    def connect_all(self):
        for connection in self.connections.keys():
            connection.connect()

    def get_state(self, state, **params):
        self.OSN_States[state].get_state_data(**params)

    def take_action(self, action, **params):
        self.OSN_Actions[action].perform_action(**params)
