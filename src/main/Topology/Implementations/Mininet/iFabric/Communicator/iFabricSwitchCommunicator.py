import sys 
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches/Communicator')
from Bmv2Communicator import Bmv2Communicator
from iFabricConnection import iFabricConnection

class iFabricSwitchCommunicator(Bmv2Communicator):
    def __init__(self, device, **params):
        Bmv2Communicator.__init__(device, **params)
        self.connections_classes.append(iFabricConnection)
    
        
