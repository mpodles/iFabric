from iFabric.iFabricTopology import iFabricTopology

class TopologyGenerator(iFabricTopology):
    
    def __init__(self, configuration):
        self.generate_switches()
        self.generate_endpoints()
        self.generate_ids_for_devices()
        self.generate_topology()
    
    def generate_switches(self):
        pass
    
    def generate_endpoints(self):
        pass

