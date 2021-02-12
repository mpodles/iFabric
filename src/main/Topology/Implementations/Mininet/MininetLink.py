from mininet.links import Link as MNLink
from Topology import Link 

class MininetLink(Link):

    def __init__(self):
        Link.__init__(self.mn_link_parameters)
        self.mn_link_instance = self.mn_link_class(self.mn_link_parameters)


