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
        self.OSNet_device.initiate_communicator()
        self.OSNet_device.OSNetCommunicator.connect()
        
    def get_state_data(self, state, **params):
        self.OSNet_device.OSNetCommunicator.get_state(state, **params)

    def take_action(self, action, **params):
        self.OSNet_device.OSNetCommunicator.take_action(action, **params)