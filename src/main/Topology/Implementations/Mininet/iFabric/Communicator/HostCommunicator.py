import sys 
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton/Communicator')
from OSNetCommunicator import OSNetCommunicator

class HostCommunicator(OSNetCommunicator):
    def __init__(self, device, **params):
        OSNetCommunicator.__init__(self, device, **params)
        self.device = device
        self.add_actions("/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches/Communicator/Actions")
        self.add_states("/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches/Communicator/States")

    def run_command(self):
        pass