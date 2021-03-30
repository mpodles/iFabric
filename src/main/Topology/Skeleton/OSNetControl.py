import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')
from OSNetTopology import OSNetTopology as Topology
from OSNetPolicy import OSNetPolicy as Policy
from OSNetFlows import OSNetFlows as Flows

class OSNetControl(object):
    #TODO: probably singleton

    def __init__(self, topology = Topology(), policy = Policy(), flows = Flows()):
        self.topology = topology
        self.policy = policy
        self.flows = flows
        self.controller_per_device = {}

    def initialize_controllers(self):
        pass

    def connect_device(self, device):
        self.controller_per_device[device].connect()

    def connect_all(self):
        for controller in self.controller_per_device.values():
            controller.connect()

    def start(self):
        for controller in self.controller_per_device.values():
            controller.start()
            

class OSNetController(object):
    def __init__(self, OSNet_device):
        self.OSNet_device = OSNet_device
        

    def connect(self):
        self.OSNet_device.initiate_communicator()
        self.OSNet_device.OSNetCommunicator.connect()
        self.get_state = self.OSNet_device.OSNetCommunicator.get_state
        self.take_action = self.OSNet_device.OSNetCommunicator.take_action

    def start(self):
        pass
        
    def get_state_data(self, state, **params):
        self.OSNetCommunicator.get_state(state, **params)

    def take_action(self, action, **params):
        self.OSNetCommunicator.take_action(action, **params)