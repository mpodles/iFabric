from OSNetTopology import OSNetTopology as Topology
from OSNetPolicy import OSNetPolicy as Policy
from OSNetFlows import OSNetFlows as Flows

class Input(object):
    #TODO: probably singleton
    topology = Topology()
    policy = Policy()
    flows = Flows()