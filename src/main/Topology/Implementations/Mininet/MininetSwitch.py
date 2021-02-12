from mininet.node import Switch
# from Skeleton import OSNetDevice
class Bmv2GrpcSwitch(Switch):
    next_grpc_port = 50051

    def __init__(self, switch):
        Switch.__init__(switch)

import functools
class OSNetDevice(object):
    ID = 1
    def __init__(self, communicator):
        self.ID = OSNetDevice.ID
        OSNetDevice.ID +=1
        self.communicator = communicator

    def run(self):
        pass

    def stop(self):
        pass

    def take_action(self, action):
        self.communicator.take_action(action)

    def get_state_data(self):
        self.communicator.get_state()

    @staticmethod
    def state_by_name(state_name):
            def state(func):
                @functools.wraps(func)
                def wrapper_state(*args,**kwargs):
                    self.communicator.states[state_name]= func
                    return func(*args, **kwargs)
                return wrapper_state
            return state

    @staticmethod
    def action_by_name(action_name):
            def action(func):
                @functools.wraps(func)
                def wrapper_action(*args,**kwargs):
                    self.communicator.actions[action_name]= func
                    return func(*args, **kwargs)
                return wrapper_action
            return action
    
class MininetSwitch(OSNetDevice,Switch):

    def __init__(self,switch,communicator):
        Switch.__init__(self,name=switch["name"])
        OSNetDevice.__init__(self,communicator)
        pass

    @OSNetDevice.state_by_name("something")
    def show_someting(self):
        print("something")
        

mn = MininetSwitch({"name":"s12"},"comm")
mn.show_someting()