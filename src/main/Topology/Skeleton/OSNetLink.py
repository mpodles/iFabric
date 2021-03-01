class OSNetLink(object):
    OSN_ID = 1
    def __init__(self, link):
        self.ID = OSNetLink.OSN_ID
        OSNetLink.OSN_ID +=1
        self.name = link.name
        self.nodes = (link.node1, link.node2)