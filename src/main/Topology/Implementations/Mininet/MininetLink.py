from mininet.links import Link
from Skeleton import OSNetLink

class MininetLink(OSNetLink, Link):

    def __init__(self,link):
        OSNetLink.__init__(link)
        Link.__init__(link)
        


