import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')
from OSNetDevice import OSNetDevice
from mininet.node import Host


class MininetEndpoint(OSNetDevice,Host):
    def __init__(self,endpoint):
        OSNetDevice.__init__(endpoint)
        Host.__init__(endpoint)
    # def config(self, **params):
    #     return super(MininetEndpoint, self).config(**params)

