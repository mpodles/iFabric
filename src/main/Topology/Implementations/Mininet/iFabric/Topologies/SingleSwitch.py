import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/iFabric')
from iFabricTopology import iFabricTopology
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/iFabric/TopologiesGenerator')
from TopologyGenerator import SingleSwitchTopologyGenerator
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
class SingleSwitch(iFabricTopology):
    def __init__(self):
        self.generator = SingleSwitchTopologyGenerator()
        self.generator.generate_topology()
        iFabricTopology.__init__(self,
                                switches = self.generator.switches, 
                                endpoints=self.generator.endpoints,
                                links = self.generator.links )
