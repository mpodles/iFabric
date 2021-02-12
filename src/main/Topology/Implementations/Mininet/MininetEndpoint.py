from mininet.net import Mininet
from mininet.node import Host
from Skeleton import OSNetDevice

class MininetHostEndpoint(Host):
    def __init__(self,endpoint_params, endpoint_class):
        Host.__init__(endpoint_class)
        self.endpoint = endpoint_class(endpoint_params)

class MininetEndpoint(OSNetDevice):
    def __init__(self,endpoint_params, endpoint_class):
        OSNetDevice.__init__(endpoint_class)
        self.endpoint = endpoint_class(endpoint_params)

    # def config(self, **params):
    #     return super(MininetEndpoint, self).config(**params)

