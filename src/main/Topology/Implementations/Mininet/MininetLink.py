from mininet.link import Link
import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton')
from OSNetLink import OSNetLink

class MininetLink(OSNetLink, Link):

    def __init__(self,link):
        OSNetLink.__init__(self, link)
        Link.__init__(self)
        


