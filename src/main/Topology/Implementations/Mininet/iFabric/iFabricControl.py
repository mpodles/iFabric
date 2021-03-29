import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton/')
from OSNetControl import OSNetControl , OSNetController
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/iFabric')
from HeaderParser import HeaderParser


# sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton/Communicator')
# from OSNetCommunicator import OSNetCommunicator

class iFabricControl(OSNetControl):
    #TODO: probably singleton

    def __init__(self, input=Input):
        self.controller_per_device = {}
        for device in Input.topology.OSN_nodes:
            self.controller_per_device[device] = OSNetController(device)

    def prepare_parser():     
        self.parser = HeaderParser(protocols_description_file_path)
                

class MainframeController(OSNetController):
    def __init__(self, OSNet_device):
        OSNetController.__init__(self, OSNet_device)

class SwitchController(OSNetController):
    def __init__(self, OSNet_device):
        OSNetController.__init__(self, OSNet_device)

    def prepare_switch(self):
        self.take_action("PrepareSwitch")

    def insert_table_entry(self, table_entry):
        self.take_action(
                "InsertTableEntry", 
                table_name = "MyIngress.Flow_classifier",
                match_fields = { "hdr.Ethernet.dstAddr": {"low": "a0:a1:a2:a3:a4:a5", "high":"a0:a1:a2:a3:a4:ff"} },
                action_name = "MyIngress.append_iFabric_header",
                action_params = {"flow_id" : 12, "node_id": 13},
                priority = 12)

    def print_table_entries(self):
        self.get_state("TableEntries")

    def start(self):
        while True:
            packetin = self.take_action("ReceivePacket")
            payload = packetin.packet.payload
            metadata = packetin.packet.metadata 
            for meta in metadata:
                metadata_id = meta.metadata_id 
                value = parser.to_bits(meta.value)
            payload = self.parser.parse_packet(payload)
            payload.fields()

class EndpointController(OSNetController):
    def __init__(self, OSNet_device):
        OSNetController.__init__(self, OSNet_device)

    def ready_endpoint(self):
        self.take_action("Command", command = "ip link set dev lo up")

    def send_packets(self):
        self.take_action("Command", command = "python tester.py")
