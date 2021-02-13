class OSNetDevice(object):
    OSN_ID = 1
    def __init__(self):
        self.ID = OSNetDevice.OSN_ID
        OSNetDevice.OSN_ID +=1
        self.OSN_States = {}
        self.OSN_Actions = {}

    def run(self):
        pass

    def stop(self):
        pass


# import functools
# class OSNetDevice(object):
#     ID = 1
#     def __init__(self, device, communicator):
#         self.ID = OSNetDevice.ID
#         OSNetDevice.ID +=1
#         self.device = device
#         self.communicator = communicator

#     def run(self):
#         pass

#     def stop(self):
#         pass

#     def take_action(self, action):
#         self.communicator.take_action(action)

#     def get_state_data(self):
#         self.communicator.get_state()

#     def state_by_name(self,state_name):
#             def state(func):
#                 @functools.wraps(func)
#                 def wrapper_state(*args,**kwargs):
#                     self.communicator.states[state_name]= func
#                     return func(*args, **kwargs)
#                 return wrapper_state
#             return state

#     def action_by_name(self,action_name):
#             def action(func):
#                 @functools.wraps(func)
#                 def wrapper_action(*args,**kwargs):
#                     self.communicator.actions[action_name]= func
#                     return func(*args, **kwargs)
#                 return wrapper_action
#             return action
    



