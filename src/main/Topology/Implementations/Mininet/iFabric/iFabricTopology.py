import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from MininetTopology import BMV2GrpcTopo
from iFabricEndpoint import iFabricEndpoint
from iFabricSwitch import iFabricSwitch
from iFabricLink import iFabricLink

class iFabricTopology(BMV2GrpcTopo):

    def __init__(self, switches, endpoints, links):
        BMV2GrpcTopo.__init__(self, switches, endpoints, links)
        self.switch_class = iFabricSwitch
        self.endpoint_class = iFabricEndpoint
        self.link_class = iFabricLink

if __name__ == "__main__":
    ift = iFabricTopology(1,2,3)

        