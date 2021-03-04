import sys 
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton/Communicator')
from OSNetAction import OSNetAction
from OSNetState import OSNetState
import imp 
import os

class OSNetCommunicator(object):
    def __init__(self, device, **params):
        self.device = device
        self.connections = {}
        self.OSN_States = {}
        self.OSN_Actions = {}

    def connect(self):
        pass    

    def disconnect(self):
        pass

    def add_actions(self, actions_folder):
        sys.path.append(actions_folder)
        for filename in os.listdir(actions_folder):
            path = os.path.join(actions_folder, filename)
            module = imp.load_source(filename, path)
            self.OSN_Actions[filename]=(OSNetAction(filename, module.get_function()))
    
    def add_states(self, states_folder):
        sys.path.append(states_folder)
        for filename in os.listdir(states_folder):
            path = os.path.join(states_folder, filename)
            module = imp.load_source(filename, path)
            self.OSN_States[filename]=(OSNetState(filename, module.get_function()))

    def get_state(self, state, **params):
        self.OSN_States[state](**params)

    def take_action(self, action, **params):
        self.OSN_Actions[action](**params)
