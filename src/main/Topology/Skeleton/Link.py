class Link(object):
    ID = 1
    def __init__(self, link, properties):
        self.ID = Link.ID
        Link.ID +=1
        self.nodes = link["devices"]
        self.name = self.generate_link_name()
        self.properties = properties
    
    def generate_link_name(self):
        return str(self.nodes[0]) + "<--->" + str(self.nodes[1])
