class Link(object):
    ID = 1
    def __init__(self, link):
        self.ID = Link.ID
        Link.ID +=1
        self.
        self.nodes = link["devices"]
        self.properties = link["properties"]
    
    # def generate_link_name(self):
    #     return str(self.nodes[0]) + "<--->" + str(self.nodes[1])
