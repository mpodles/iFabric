class SwitchData(object):
    def __init__(self, name, **params):
        self.name = name
        self.interfaces = {}
        self.type = "switch"