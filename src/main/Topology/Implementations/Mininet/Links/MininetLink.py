from mininet.links import Link as mnlink
from topology import Link as topolink

class MininetLink(topolink,mnlink):

    def __init__(self,link_parameters):
        self.generate_topology_link_based_on_parameters(link_parameters)
        self.generate_mininet_link_based_on_parameters(link_parameters)

    def generate_topology_link_based_on_parameters(self,link_parameters):
        pass

    def generate_mininet_link_based_on_parameters(self,link_parameters):
        pass
