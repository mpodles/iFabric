from mininet.link import Link
import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')
from OSNetLink import OSNetLink
import rstr

class MininetLink(OSNetLink, Link):

    def __init__(self, *args, **kwargs):
        link = kwargs["params_object"]
        OSNetLink.__init__(self, link)
        try:
            addr1 = link.node1.mac
        except:
            addr1 = rstr.xeger('[0-9A-F]0:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]')
        try:
            addr2 = link.node2.mac
        except:
            addr2 = rstr.xeger('[0-9A-F]0:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]')

        Link.__init__(self, 
                    node1 = args[0], 
                    node2 = args[1],
                    port1 = kwargs["port1"],
                    port2 = kwargs["port2"],
                    addr1 = addr1,
                    addr2 = addr2)
        