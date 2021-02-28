class LinkData(object):

    def __init__(self, name, latency, bandwidth, **params):
        self.name = name
        self.latency = latency
        self.bandwidth = bandwidth