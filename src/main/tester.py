from mininet.link import Link as MNLink_Class
from mininet.link import TCLink
# from Topology import Link 

class MininetLink(MNLink_Class):

    def __init__(self,link , mn_link_class= MNLink_Class):
        mn_link_class.__init__(mn_link_class())

class nextLink(MininetLink):
    def __init__(self):
        MininetLink.__init__(self,1,TCLink)


nextLink()
pass
