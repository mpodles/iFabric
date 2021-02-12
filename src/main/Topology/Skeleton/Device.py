class Device(object):
    ID = 1
    def __init__(self, device):
        self.ID = Device.ID
        Device.ID +=1
        self.name = device["name"]
        self.communicator = device["communicator"]

    def run(self):
        pass

    def stop(self):
        pass

    def take_action(self, action):
        self.communicator.take_action(action)

    def get_state_data(self):
        self.communicator.get_state()
    



