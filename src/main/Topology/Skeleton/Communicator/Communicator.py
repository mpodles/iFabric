class Communicator(object):
    def __init__(self, states, actions):
        self.states = states
        self.actions = actions
    
    def get_state(self, state, **params):
        self.states[state].get_state_data(**params)

    def take_action(self, action, **params):
        self.actions[action].perform_action(**params)
