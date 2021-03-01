from mininet.link import TCLink
import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet')
from MininetLink import MininetLink

class iFabricLink(MininetLink):
    def __init__(self, link):
        MininetLink.__init__(self, link)

