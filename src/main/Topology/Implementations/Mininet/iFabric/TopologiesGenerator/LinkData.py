class LinkData(object):

    def __init__(self, node1, node2, name=None, latency=None, bandwidth=None, **params):
        self.name = name
        self.latency = latency
        self.bandwidth = bandwidth
        self.node1 = node1
        self.node2 = node2