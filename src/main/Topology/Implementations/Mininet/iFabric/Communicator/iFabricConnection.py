# import sys
# sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/Switches/Communicator')
# from Bmv2Connection import Bmv2Connection
# sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton/Communicator')
# from OSNetAction import OSNetAction
# from OSNetState import OSNetState

# from importlib import import_module
# import os
# class iFabricConnection(Bmv2Connection):
#     def __init__(self, communicator):
#         Bmv2Connection.__init__(self, communicator)
#         self.add_actions()
#         self.add_states()

#     def add_actions(self):
#         for filename in os.listdir("./Actions"):
#             module = import_module(filename, "Actions")
#             self.OSN_Actions.append(OSNetAction(filename, module.perform_action))
    
#     def add_states(self):
#         for filename in os.listdir("./States"):
#             module = import_module(filename, "States")
#             self.OSN_State.append(OSNetState(filename, module.get_state_data))
        
    