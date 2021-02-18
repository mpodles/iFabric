class OSNetLink(object):
    OSN_ID = 1
    def __init__(self, link):
        self.ID = OSNetLink.OSN_ID
        OSNetLink.OSN_ID +=1
        self.name = link["name"]
        self.nodes = link["devices"]
        self.properties = link["properties"]
    
    # def generate_link_name(self):
    #     return str(self.nodes[0]) + "<--->" + str(self.nodes[1])
