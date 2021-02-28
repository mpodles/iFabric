class OSNetCommunicator(object):
    def __init__(self, connections_with_states, connections_with_actions):
        self.connections_with_states = connections_with_states
        self.connections_with_actions = connections_with_actions

        self.connections = set( 
            [state for state in self.connections_with_states.keys()] +
            [action for action in self.connections_with_actions.keys()])
        
        self.OSN_States = []
        for conn in connections_with_states:
            for state in conn:
                self.OSN_States.append(state)
        
        self.OSN_Actions = []
        for conn in connections_with_actions:
            for action in conn:
                self.OSN_Actions.append(action)

    def connect(self, connection):
        connection.connect()

    def disconnect(self, connection):
        connection.disconnect()
            
    def connect_all(self):
        for connection in self.connections:
            connection.connect()

    def get_state(self, state, **params):
        self.OSN_States[state].get_state_data(**params)

    def take_action(self, action, **params):
        self.OSN_Actions[action].perform_action(**params)
