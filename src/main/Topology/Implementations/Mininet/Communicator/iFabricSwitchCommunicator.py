import sys 
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches/Communicator')
from Bmv2Communicator import Bmv2Communicator

class iFabricSwitchCommunicator(Bmv2Communicator):
    def __init__(self, **params):
        Bmv2Communicator.__init__(**params)
        
