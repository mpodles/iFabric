from mininet.node import Switch
from Skeleton import OSNetDevice

class MininetSwitch(OSNetDevice):

    def __init__(self,switch_class):
        Device.__init__(switch_class)
        self.switch = switch_class.__init__(dpid= str(Device.ID))
    #     