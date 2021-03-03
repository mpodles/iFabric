from mininet.link import Link
import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')
from OSNetLink import OSNetLink
import rstr

class MininetLink(OSNetLink, Link):

    def __init__(self, *args, **kwargs):
        link = kwargs["params_object"]
        OSNetLink.__init__(self, link)
        Link.__init__(self, 
                    node1 = args[0], 
                    node2 = args[1],
                    port1 = kwargs["port1"],
                    port2 = kwargs["port2"],
                    addr1 = addr1,
                    addr2 = addr2)
        