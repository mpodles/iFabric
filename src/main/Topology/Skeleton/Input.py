from OSNetTopology import OSNetTopology as Topology
from OSNetPolicy import OSNetPolicy as Policy
from OSNetFlows import OSNetFlows as Flows

class Input(object):
    #TODO: probably singleton
    def __init__(self, topology = Topology(), policy = Policy(), flows = Flows())
        self.topology = topology
        self.policy = policy
        self.flows = flows