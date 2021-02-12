from mininet.net import Mininet
from mininet.node import Host
from.

class MininetEndpoint(Device, Host):
    def config(self, **params):
        return super(MininetEndpoint, self).config(**params)


