from mininet.node import Switch
import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')
from OSNetDevice import OSNetDevice

    
    
class MininetSwitch(OSNetDevice,Switch):

    def __init__(self,switch):
        OSNetDevice.__init__(self, device = switch)
        Switch.__init__(self, self.device.name, dpid = str(self.OSN_ID))

    def run(self):
        pass

    def stop(self):
        pass
        