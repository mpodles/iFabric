import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches')
from Bmv2GrpcSwitch import Bmv2GrpcSwitch
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Communicator')
from iFabricSwitchCommunicator import iFabricSwitchCommunicator


class iFabricSwitch(Bmv2GrpcSwitch):
    def __init__(self, switch, **params):
        Bmv2GrpcSwitch.__init__(self, switch, **params)
        self.OSNetCommunicator_class = iFabricSwitchCommunicator


