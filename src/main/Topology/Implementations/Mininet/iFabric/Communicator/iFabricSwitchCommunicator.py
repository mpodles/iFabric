import sys 
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches/Communicator')
from Bmv2Communicator import Bmv2Communicator

class iFabricSwitchCommunicator(Bmv2Communicator):
    def __init__(self, device, **params):
        Bmv2Communicator.__init__(self, device, **params)
        # self.add_actions("/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/iFabric/Communicator/Actions")
        # self.add_states("/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/iFabric/Communicator/States")
