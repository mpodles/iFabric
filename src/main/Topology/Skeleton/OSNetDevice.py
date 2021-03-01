import sys 
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton/Communicator')
from OSNetCommunicator import OSNetCommunicator
class OSNetDevice(object):
    next_OSN_ID = 1
    def __init__(self,device):
        self.OSN_ID = OSNetDevice.next_OSN_ID
        OSNetDevice.next_OSN_ID +=1
        self.device = device
        self.OSNetCommunicator = None
        self.OSNetCommunicator_class = OSNetCommunicator

    def initiate_communicator(self):
        self.OSNetCommunicator = self.OSNetCommunicator_class(self)
