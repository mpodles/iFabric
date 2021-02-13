import src/main/Topology/Skeleton/OSNetTopology.py 
import endpoints.MininetEndpoint
import switches.Bmv2GrpcSwitch
from mininet.node import Switch
from mininet.links import Link
from mininet.topology import Topo
from Switches import Bmv2GrpcSwitch

class BMV2GrpcTopo(Topo):
    def __init__(self, nodes, switches, links, node_links, log_dir, bmv2_exe, pcap_dir, **opts):
        Topo.__init__(self, **opts)
        self.log_dir = log_dir
        self.pcap_dir = pcap_dir
        self.bmv2_exe = bmv2_exe
        self.already_added_links = []

        self.add_switches(switches)
        self.add_nodes(nodes)
        self.add_links(links, node_links)

    def add_switches(self, switches):
        for sw, params in switches.iteritems():
            if "program" in params:
                switchClass = configureP4Switch(
                        sw_path=self.bmv2_exe,
                        json_path=params["program"],
                        log_console=True,
                        pcap_dump=self.pcap_dir)
            else:
                # add default switch
                switchClass = None
            self.addSwitch(sw, log_file="%s/%s.log" %(self.log_dir, sw), cls=Bmv2GrpcSwitch)
    
    def add_nodes(self, nodes):
        for node, interfaces in nodes.items():
            self.addNode(node, interfaces =interfaces)


    def add_links(self, switch_links, node_links):
        for node, links in node_links.items():
            for node_link in links:
                sw, sw_port, node_port = node_link["connected_switch"], node_link["connected_port"], node_link["port"]
                self.addLink(node, sw,
                         delay='0ms', bw=None,
                         port1=node_port, port2=sw_port)

        for sw, links in switch_links.items():
            for switch_link in links["switchports"]:
                sw_port, connected_sw, connected_sw_port = switch_link["port"], switch_link["connected_switch"], switch_link["connected_port"]
                if not self.link_already_added(sw, sw_port, connected_sw, connected_sw_port):
                    self.addLink(sw, connected_sw,
                        port1=sw_port, port2=connected_sw_port,
                        delay='0ms', bw=None)

    def link_already_added(self, sw, sw_port, connected_sw, connected_sw_port):
        link1 = ((sw,sw_port),(connected_sw,connected_sw_port))
        link2 = ((connected_sw,connected_sw_port),(sw,sw_port))
        if link1 in self.already_added_links or link2 in self.already_added_links:
            return True
        else: 
            self.already_added_links.append(link1)
            self.already_added_links.append(link2)
            return False

class iFabricTopology(BMV2GrpcTopology):
    pass
class MininetTopology(OSNetTopology,Topology):
    def __init__(self,
                switches,
                endpoints,
                links,
                mn_topo_class = Topology):
                
        mn_topo_class.__init__()
        # mn_topo_class =
        self.switches = switches
        self.endpoints = endpoints
        self.links = links
        self.mn_topo_class = mn_topo_class
        self.generate_mininet_topo()
        OSNetTopology.__init__()

    def generate_nodes(self):
        nodes = []
        for switch in self.switches:
            nodes.append(OSNetDevice(device = switch))

        for endpoint in self.endpoints:
            nodes.append(self.endpoint_class(endpoint))

        return nodes

    def generate_links(self):
        links = []
        for link in self.links:
            links.append(OSNetLink(link = link))

        for endpoint in self.endpoints:
            nodes.append(self.endpoint_class(endpoint))

        return nodes

    def generate_topo(self):
        pass

    def generate_mininet_topo(self):
        self.mn_topology = self.mn_topo_class(self.switches,self.endpoints,self.links)

    # def generate_switches(self):
    #     self.topology.switches.add_node("SingleSwitch")
    #     self.topology.mininet_topo.addSwitch(
    #         "SingleSwitch", 
    #         cls=self.topology.switch_class)
    
    # def generate_endpoints(self):
    #     for ep_nr in range(1,self.endpoints+1):
    #         endpoint_name = "EP_" + str(ep_nr)
    #         self.topology.endpoints.add_node(endpoint_name)
    #         self.topology.mininet_topo.addNode(
    #             endpoint_name)

    # def generate_groups(self):
    #     groups_count = self.endpoints / self.avg_group_size
    #     for gr_nr in range(1, groups_count + 1):
    #         endpoints = ["EP_" + str(self.avg_group_size*gr_nr - i) for i in range(self.avg_group_size)]
    #         self.topology.groups.add_node("Group_" + str(gr_nr), endpoints = endpoints)

    # def generate_topology_with_endpoints(self):
    #     switch_interface = 1
    #     for endpoint in self.topology.endpoints.nodes:
    #         info = {"cls" : self.topology.endpoint_class}
    #         interfaces = {}
    #         for endpoint_interface in range(self.ports_per_endpoint):
    #             switch_interface += 1
    #             self.topology.mininet_topo.addLink(
    #                 "SingleSwitch",
    #                 endpoint, 
    #                 delay='0ms',
    #                 bw=None,
    #                 port1=switch_interface,
    #                 port2=endpoint_interface)
    #             interface_name = endpoint + "-eth" + str(endpoint_interface)
    #             interfaces[interface_name] = {
    #                 "ip": self.generate_ip_addressing(endpoint),
    #                 "mac": self.generate_mac_addressing(endpoint),
    #                 "connected_to": "SingleSwitch",
    #                 "connected_on": switch_interface}
                    
    #         info["interfaces"] = interfaces
    #         self.topology.mininet_topo.setNodeInfo(endpoint, info = info)

    #         self.topology.switches_with_endpoints.add_edge(
    #                 "SingleSwitch",
    #                 endpoint, 
    #                 weight=1, 
    #                 interfaces= interfaces)

    # def generate_topology_with_groups(self):
    #     #TODO: finish this
    #     switch_interface = 1
    #     # for group in self.topology.groups.nodes:
    #     #     for endpoint_interface in range(self.ports_per_endpoint):
    #     #         self.topology.switches_with_endpoints.add_edge(
    #     #             "SingleSwitch",
    #     #             group, 
    #     #             weight=1, 
    #     #             interfaces= [{"SingleSwitch": switch_interface , endpoint: endpoint_interface}])

    
    # def generate_ip_addressing(self, endpoint):
    #     if self.ip_addressing == "random":
    #         return self.generate_random_ip_addressing()

    # def generate_random_ip_addressing(self):
    #     return str(random.randint(10, 223)) + "." + str(random.randint(0, 255))+ "." +str(random.randint(0, 255))+ "." +str(random.randint(0, 255))

    # def generate_mac_addressing(self, endpoint):
    #     if self.ip_addressing == "random":
    #         return self.generate_random_mac_addressing()

    # def generate_random_mac_addressing(self):
    #     #TODO: verify rstr licence
    #     random_mac=rstr.xeger('[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]:[0-9A-F][0-9A-F]')
    #     return random_mac
    
