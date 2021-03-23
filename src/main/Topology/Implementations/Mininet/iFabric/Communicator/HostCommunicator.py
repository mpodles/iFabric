import sys 
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Communicator')
from MininetCommunicator import MininetCommunicator

class HostCommunicator(MininetCommunicator):
    def __init__(self, device, **params):
        MininetCommunicator.__init__(self, device, **params)
