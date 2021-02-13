from mininet.node import Switch
# from Skeleton import OSNetDevice
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

    #             self.states[name] = Action()
    #     return Action_generator



    # @State("something")
    # def show_someting(self):
    #     print("something")
    
    
class MininetSwitch(OSNetDevice,Switch):

    def __init__(self,switch):
        OSNetDevice.__init__(self)
        Switch.__init__(self,name=switch["name"])
        pass


mn = MininetSwitch({"name":"s12"})