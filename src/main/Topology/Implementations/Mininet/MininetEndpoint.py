import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')
from OSNetDevice import OSNetDevice
from mininet.node import Host


class MininetEndpoint(OSNetDevice,Host):
    def __init__(self,endpoint, **params):
        endpoint = params["params_object"]
        OSNetDevice.__init__(self, endpoint)
        Host.__init__(self, endpoint.name)
    
    def run(self):
        pass

    def stop(self):
        pass

