import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')
from Input import Input
# sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton/Communicator')
# from OSNetCommunicator import OSNetCommunicator

class OSNetControl(object):
    #TODO: probably singleton

    def __init__(self, input=Input):
        self.controller_per_device = {}
        for device in Input.topology.OSN_nodes:
            self.controller_per_device[device] = OSNetController(device)
            

class OSNetController(object):
    def __init__(self, OSNet_device):
        self.OSNet_device = OSNet_device

    def connect(self):
        self.OSNet_device.OSNetCommunicator.connect_all()
