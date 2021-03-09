class OSNetState(object):
    def __init__(self, name, state_function, **params):
        self.name = name
        self.state_function = state_function
        self.latest_state_data = None
        self.state_log = None

    def __call__(self, communicator, **params):
        return self.state_function(self, communicator, **params)

    def get_state_data(self):
        pass