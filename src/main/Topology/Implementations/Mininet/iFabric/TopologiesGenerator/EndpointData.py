class EndpointData(object):
    def __init__(self, name, **params):
        self.name = name
        self.interfaces = {}
        self.type = "endpoint"
        self.interfaces_by_number = {}
