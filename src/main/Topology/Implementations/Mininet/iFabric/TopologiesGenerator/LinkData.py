class LinkData(object):

    def __init__(self, name, latency, bandwidth, node1, node2, **params):
        self.name = name
        self.latency = latency
        self.bandwidth = bandwidth
        self.node1 = node1
        self.node2 = node2