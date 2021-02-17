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
       
   

        
