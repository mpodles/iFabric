class OSNetDevice(object):
    next_OSN_ID = 1
    def __init__(self,switch):
        self.OSN_ID = OSNetDevice.next_OSN_ID
        OSNetDevice.next_OSN_ID +=1
        self.name = switch
        self.OSN_States = {}
        self.OSN_Actions = {}

    def run(self):
        pass

    def stop(self):
        pass