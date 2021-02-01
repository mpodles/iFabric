import concurrent.futures

class Agent():

    def __init__(self, topology, other_agents):
        self.topology = topology
        self.other_agents = other_agents
    

    def start(self):
        try:
            self.initialize_operation()
            self.operate()
            self.close_operation()
        except Exception as e:
            print e
        finally:
            self.close_operation()
    
    def initialize_operation(self):
        pass

    def operate(self):
        pass

    def close_operation(self):
        pass