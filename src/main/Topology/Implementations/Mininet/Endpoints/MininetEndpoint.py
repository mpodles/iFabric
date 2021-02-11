from mininet.net import Mininet
from mininet.node import Switch, Host

class MininetEndpoint(Host):
    def config(self, **params):
        return super(MininetEndpoint, self).config(**params)


