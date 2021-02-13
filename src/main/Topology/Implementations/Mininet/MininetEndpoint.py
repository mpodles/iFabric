from mininet.node import Host
from Skeleton import OSNetDevice

class MininetEndpoint(OSNetDevice,Host):
    def __init__(self,endpoint):
        OSNetDevice.__init__(endpoint)
        Host.__init__(endpoint)
    # def config(self, **params):
    #     return super(MininetEndpoint, self).config(**params)

