class OSNetDevice(object):
    next_OSN_ID = 1
    def __init__(self,device):
        self.OSN_ID = OSNetDevice.next_OSN_ID
        OSNetDevice.next_OSN_ID +=1
        self.name = device.name
        self.OSNetCommunicator = device.communicator 

    def run(self):
        pass

    def stop(self):
        pass