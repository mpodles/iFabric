import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches')
from Bmv2GrpcSwitch import Bmv2GrpcSwitch


class iFabricSwitch(Bmv2GrpcSwitch):
    def __init__(self, switch):
        Bmv2GrpcSwitch.__init__(self, switch)
        self.device_id = OSNetDevice.OSN_ID
        self.states = {}
        self.actions = {}
        self.compiled_program = "iFabric"

