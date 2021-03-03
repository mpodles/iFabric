class LinkData(object):

    def __init__(self, node1, node2, int1, int2, name=None, latency=None, bandwidth=None, **params):
        self.name = name
        self.latency = latency
        self.bandwidth = bandwidth
        self.node1 = node1
        self.node2 = node2
        self.int1 = int1
        self.int2 = int2