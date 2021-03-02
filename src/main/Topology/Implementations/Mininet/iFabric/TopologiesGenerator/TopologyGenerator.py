import random
import rstr
import os 
import json
from SwitchData import SwitchData
from LinkData import LinkData
from EndpointData import EndpointData
class iFabricTopologyGenerator(object):
    def __init__(self, topology_description_file_path):
        self.topology_description_file_path = topology_description_file_path
        self.get_configuration()

    
    def get_configuration(self):
        self.configuration =  json.loads(open(self.topology_description_file_path).read())

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
    
    def __init__(self, topology_description_file_path):
        iFabricTopologyGenerator.__init__(self, topology_description_file_path)
        self.switches = {}
        self.endpoints_count = self.configuration["endpoints"]
        self.endpoints = {}
        self.links = {}
        self.groups = {}
        self.avg_group_size = self.configuration ["avg_group_size"]
        self.ports_per_endpoint = self.configuration ["ports_per_endpoint"]
        self.ip_addressing = self.configuration ["ip_addressing"]
        self.mac_addressing = self.configuration ["mac_addressing"]
    
    def generate_switches(self):
        self.switches["SingleSwitch"] = SwitchData("SingleSwitch")
    
    def generate_endpoints(self):
        for ep_nr in range(1,self.endpoints_count+1):
            endpoint_name = "EP_" + str(ep_nr)
            self.endpoints[endpoint_name] = EndpointData(endpoint_name, self.generate_ip_address(endpoint_name) , self.generate_mac_address(endpoint_name) )

    def generate_links(self):
        for endpoint in self.endpoints.values():
            link_name = "SingleSwitch" + " - " + endpoint.name
            self.links[link_name] = LinkData(link_name, "1ms", "1000Mbs", endpoint, self.switches["SingleSwitch"])

    def generate_groups(self):
        groups_count = self.endpoints_count / self.avg_group_size
        for gr_nr in range(1, groups_count + 1):
            endpoints = [self.endpoints["EP_" + str(self.avg_group_size*gr_nr - i)] for i in range(self.avg_group_size)]
            self.groups["Group_" + str(gr_nr)] = endpoints
  
    def generate_ip_address(self, endpoint):
        if self.ip_addressing == "random":
            return self.generate_random_ip_address()

    def generate_random_ip_address(self):
        return str(random.randint(10, 223)) + "." + str(random.randint(0, 255))+ "." +str(random.randint(0, 255))+ "." +str(random.randint(0, 255))

    def generate_mac_address(self, endpoint):
        if self.ip_addressing == "random":
            return self.generate_random_mac_address()

    def generate_random_mac_address(self):
        #TODO: verify rstr licence
        random_mac=rstr.xeger('[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]')
        return random_mac


