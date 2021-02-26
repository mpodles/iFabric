import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')

import Input

class OSNetController(object):
    def __init__(self, OSNet_device):
        self.OSNet_device = OSNet_device

    def device_connection(self):
        