from mininet.node import Switch
from Topology import Device

class MininetSwitch(Device,Switch):

    def __init__(self,switch):
        Device.__init__(self,switch)
        self.generate_device_based_on_parameters(switch_parameters)
        self.generate_mininet_switch_based_on_parameters(switch_parameters)

    def generate_device_based_on_parameters(self,switch_parameters):
        pass

    def generate_mininet_switch_based_on_parameters(self,switch_parameters):
        pass
