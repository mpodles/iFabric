class OSNetDevice(object):
    OSN_ID = 1
    def __init__(self,switch):
        self.ID = OSNetDevice.OSN_ID
        OSNetDevice.OSN_ID +=1
        self.name = switch
        self.OSN_States = {}
        self.OSN_Actions = {}

    def run(self):
        pass

    def stop(self):
        pass
    # @classmethod #TODO: better python integration with decorators?
    # def State(name):
    #     def State_generator(state_function):
    #         def function_wrapper(self, *args, **kwargs):
    #             class State(object):
    #                 def __init__(self):
    #                     self.name = name
    #                     self.state_function = state_function

    #                 def get_state_data(self):
    #                     self.__call__()                        

    #                 def __call__(self):
    #                     self.state_function(*args, **kwargs)


    #             self.OSN_States[name] = State()
    #     return State_generator

    # @classmethod
    # def Action(name):
    #     def Action_generator(action_function):
    #         def function_wrapper(self, *args, **kwargs):
    #             class Action(object):
    #                 def __init__(self):
    #                     self.name = name
    #                     self.action_function = action_function

    #                 def take_action(self):
    #                     self.__call__()                        

    #                 def __call__(self):
    #                     self.action_function(*args, **kwargs)

    #             self.OSN_Actions[name] = Action()
    #     return Action_generator



    # @State("something")
    # def show_someting(self):
    #     print("something")    

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
    



