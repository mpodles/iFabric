from mininet.node import Switch
from Skeleton import OSNetDevice
    
    
class MininetSwitch(OSNetDevice,Switch):

    def __init__(self,switch):
        OSNetDevice.__init__(self,name=switch["name"])
        Switch.__init__(self,name=switch["name"])
        pass


mn = MininetSwitch({"name":"s12"})