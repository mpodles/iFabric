from mininet.node import Switch
import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')
from OSNetDevice import OSNetDevice

    
    
class MininetSwitch(OSNetDevice,Switch):

    def __init__(self, switch, **params):
        OSNetDevice.__init__(self, device = params["params_object"])
        Switch.__init__(self, switch, dpid = str(self.OSN_ID))

    def run(self):
        pass

    def stop(self):
        pass
        