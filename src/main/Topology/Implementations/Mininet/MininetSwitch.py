from mininet.node import Switch
import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')
from OSNetDevice import OSNetDevice

    
    
class MininetSwitch(OSNetDevice,Switch):

    def __init__(self,switch):
        OSNetDevice.__init__(self,switch)
        Switch.__init__(self,switch, dpid = str(OSNetDevice.OSN_ID))
        