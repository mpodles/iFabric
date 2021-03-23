import sys 
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton/Communicator')
from OSNetCommunicator import OSNetCommunicator

import os


class MininetCommunicator(OSNetCommunicator):
    def __init__(self, device, **params):
        OSNetCommunicator.__init__(self, device, **params)
        self.device = device
        self.device_data = device.device_data
        self.add_actions("/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Communicator/Actions")
        self.add_states("/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Communicator/States")
     
    def connect(self):
        pass

    def disconnect(self):
        pass
