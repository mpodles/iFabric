from mininet.link import TCLink
from Mininet import MininetLink

class iFabricLink(MininetLink):
    def __init__(self,mn_link):
        self.mn_link_class = mn_link["mn_link_class"]
        self.mn_link_parameters = mn_link["parameters"]
        MininetLink.__init__()

    def calculate_cost(self):
