class OSNetTopology(object):
    def __init__(self):        
        self.OSN_nodes = None
        self.OSN_links = None

    def generate_topology(self):        
        self.OSN_nodes = self.generate_nodes()
        self.OSN_links = self.generate_links()

        
    def generate_nodes(self):
        pass

    def generate_links(self):
        pass
       
    def node(self, node_name):
        return self.OSN_nodes[node_name]

    def link(self, link_name):
        return self.OSN_links[link_name]


        
