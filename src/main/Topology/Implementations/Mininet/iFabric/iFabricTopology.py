from Mininet import BMV2GrpcTopo
from iFabric import iFabricSwitch, iFabricEndpoint, iFabricLink

class iFabricTopology(BMV2GrpcTopo):

    def __init__(self, nodes, switches, links, node_links, log_dir, p4_code_path, p4_json_path, p4runtime_info_path, pcap_dir, **params):
        BMV2GrpcTopo.__init__()
        self.switch_class = iFabricSwitch
        self.endpoint_class = iFabricEndpoint
        self.link_class = iFabricLink

        