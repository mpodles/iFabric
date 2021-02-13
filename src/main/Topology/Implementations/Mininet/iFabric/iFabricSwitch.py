from mininet.net import Mininet
from mininet.node import Switch, Host
from mininet.moduledeps import pathCheck
from mininet.log import info, error, debug
import tempfile
from time import sleep
import psutil
import os
import functools
from Mininet.Switches import Bmv2GrpcSwitch
from Skeleton import OSNetDevice

# def state_by_name(state_name):
#         def state(func):
#             @functools.wraps(func)
#             def wrapper_state(*args,**kwargs):
#                 self.states[state_name]= func
#                 return func(*args, **kwargs)
#             return wrapper_state
#         return state

# def action_by_name(action_name):
#         def action(func):
#             @functools.wraps(func)
#             def wrapper_action(*args,**kwargs):
#                 self.actions[action_name]= func
#                 return func(*args, **kwargs)
#             return wrapper_state
#         return action
class iFabricSwitch(Bmv2GrpcSwitch):
    def __init__(self, switch):
        Bmv2GrpcSwitch.__init__(self, switch)
        self.states = {}
        self.actions = {}
        self.compiled_program = "iFabric"
        
        
    # @OSNetDevice.action_by_name("set_forwarding")
    # def set_forwarding_ports(self, ports):
    #     self.push_table_to_switch(self.buildTableEntry(ports))

    # def push_table_to_switch(self,table):
    #     pass

    # def buildTableEntry(self,ports):
    #     pass

    # @OSNetDevice.state_by_name("flow_state")
    # def get_flow_state(self,flow):
    #     pass
