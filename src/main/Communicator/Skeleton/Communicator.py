class Communicator(object):
    def __init__(self):
        self.states = {}
    
    def get_state(self, state, **params):
        self.states[state].get_state_data(**params)
