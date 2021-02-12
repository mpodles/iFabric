class OSNetDevice(object):
    ID = 1
    def __init__(self, device, communicator):
        self.ID = OSNetDevice.ID
        OSNetDevice.ID +=1
        self.device = device
        self.communicator = communicator

    def run(self):
        pass

    def stop(self):
        pass

    def take_action(self, action):
        self.communicator.take_action(action)

    def get_state_data(self):
        self.communicator.get_state()
    



