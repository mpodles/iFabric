# from iFabric.iFabricTopology import iFabricTopology
import random
import rstr
import os 
import json
class iFabricTopologyGenerator(object):
    def __init__(self):
        pass

    def generate_topology(self):
        self.generate_switches()
        self.generate_endpoints()
        self.generate_links()
        self.generate_groups()

    def generate_switches(self):
        pass

    def generate_endpoints(self):
        pass

    def generate_links(self):
        pass
    
    def generate_groups(self):
        pass

class SingleSwitchTopologyGenerator(iFabricTopologyGenerator):
    
    def __init__(self):
        iFabricTopologyGenerator.__init__(self)
        self.get_configuration()
        self.switches = []
        self.endpoints_count = self.configuration["endpoints"]
        self.endpoints = []
        self.links = []
        self.groups = {}
        self.avg_group_size = self.configuration ["avg_group_size"]
        self.ports_per_endpoint = self.configuration ["ports_per_endpoint"]
        self.ip_addressing = self.configuration ["ip_addressing"]
        self.mac_addressing = self.configuration ["mac_addressing"]

    def get_configuration(self):
        Path = "/home/mpodles/iFabric/src/main/configuration_files/topology_description_test.json"
        self.configuration =  json.loads(open(Path).read())
    
    def generate_switches(self):
        self.switches.append("SingleSwitch")
    
    def generate_endpoints(self):
        for ep_nr in range(1,self.endpoints_count+1):
            endpoint_name = "EP_" + str(ep_nr)
            self.endpoints.append(endpoint_name)

    def generate_links(self):
        for endpoint in self.endpoints:
            self.links.append(("SingleSwitch",endpoint))

    def generate_groups(self):
        groups_count = self.endpoints_count / self.avg_group_size
        for gr_nr in range(1, groups_count + 1):
            endpoints = ["EP_" + str(self.avg_group_size*gr_nr - i) for i in range(self.avg_group_size)]
            self.groups["Group_" + str(gr_nr)] = endpoints
  
    def generate_ip_addressing(self, endpoint):
        if self.ip_addressing == "random":
            return self.generate_random_ip_addressing()

    def generate_random_ip_addressing(self):
        return str(random.randint(10, 223)) + "." + str(random.randint(0, 255))+ "." +str(random.randint(0, 255))+ "." +str(random.randint(0, 255))

    def generate_mac_addressing(self, endpoint):
        if self.ip_addressing == "random":
            return self.generate_random_mac_addressing()

    def generate_random_mac_addressing(self):
        #TODO: verify rstr licence
        random_mac=rstr.xeger('[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]')
        return random_mac


