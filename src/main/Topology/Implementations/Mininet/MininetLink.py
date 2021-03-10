from mininet.link import Link
import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')
from OSNetLink import OSNetLink
import rstr

class MininetLink(OSNetLink, Link):

    def __init__(self, *args, **kwargs):
        link = kwargs["params_object"]
        OSNetLink.__init__(self, link, args[0], args[1])
        port1 = int(link.int1.split("-")[-1])
        port2 = int(link.int2.split("-")[-1])
        Link.__init__(self, 
                    node1 = args[0], 
                    node2 = args[1],
                    intfName1 = link.int1,
                    intfName2 = link.int2,
                    port1 = port1,
                    port2 = port2,
                    addr1 = link.node1.interfaces[link.int1]["mac"],
                    addr2 = link.node2.interfaces[link.int2]["mac"])
        