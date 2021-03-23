import os
import json
import argparse
import timeit
import re
from time import sleep
import threading
import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/iFabric/Topologies')
from SingleSwitch import SingleSwitch
import traceback
from mininet.cli import CLI
# from scapy.all import *


main_project_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(main_project_directory)

def parse_structure():
    with open(os.path.join(main_project_directory, "folders_and_files.json"), "r") as structure_file:
        structure = json.loads(structure_file.read())
    return structure

structure = parse_structure()


build_folder = structure["build_folder"]
pcaps_folder = structure["pcaps_folder"]
logs_folder = structure["logs_folder"]
topology_file = structure["topology_file"]
p4_file_name = structure["p4_code_file_name"]
p4runtime_file_name = structure["p4runtime_file_name"]
compiled_p4_file_name = structure["compiled_p4_file_name"]
protocols_description_file_name = structure["protocols_description_file"]
p4template = structure["p4_code_template"]
configuration_folder = structure["configuration_folder"]
topology_description_file = structure["topology_description_file"]
protocols_folder = structure["protocols_folder"]
flows_file = structure["flows_file"]
flows_ids_file = structure["flows_ids_file"]
bmv2_exe = structure["BMV2_SWITCH_EXE"]
policy_file = structure["policy_file"]
switches_connections_file = structure["switches_connections_file"]


build_path = os.path.join(main_project_directory, build_folder)
topology_file_path = os.path.join(main_project_directory, build_folder, topology_file)
topology_description_file_path = os.path.join(main_project_directory, configuration_folder, topology_description_file)
logs_path = os.path.join(main_project_directory, build_folder, logs_folder)
pcaps_path = os.path.join(main_project_directory, build_folder, pcaps_folder)
p4_code_file_path = os.path.join(main_project_directory, build_folder, p4_file_name)
p4runtime_info_file_path = os.path.join(main_project_directory, build_folder, p4runtime_file_name)
p4_json_file_path = os.path.join(main_project_directory, build_folder, compiled_p4_file_name)
configuration_folder_path =  os.path.join(main_project_directory, configuration_folder)
protocols_folder_path = os.path.join(main_project_directory, build_folder, protocols_folder)
protocols_description_file_path = os.path.join(main_project_directory, configuration_folder, protocols_description_file_name)
p4_template_file_path =  os.path.join(main_project_directory, configuration_folder, p4template)
flows_file_path =  os.path.join(main_project_directory, build_folder, flows_file)
runtimes_files_path = os.path.join(main_project_directory, build_folder)
flows_ids_file_path = os.path.join(main_project_directory, build_folder, flows_ids_file)  
policy_file_path = os.path.join(main_project_directory, build_folder, policy_file)
switches_connections_file_path = os.path.join(main_project_directory, build_folder, switches_connections_file)

def prepare_folders():
    os.system(" ".join(["mkdir -p", build_path, pcaps_path, logs_path, protocols_folder_path]))

def prepare_topology():
    sstg = SingleSwitch(
        topology_description_file_path = topology_description_file_path,
        p4_template_file_path = p4_template_file_path, 
        p4_code_file_path = p4_code_file_path, 
        protocols_description_file_path = protocols_description_file_path, 
        protocols_folder_path = protocols_folder_path,
        p4runtime_info_file_path =p4runtime_info_file_path, 
        p4_json_file_path = p4_json_file_path, 
        log_dir = logs_path, 
        pcap_dir = pcaps_path
        )
    return sstg
    
# def generate_flows():
#     flows_generator = f_gen.DestinationFlowGenerator(
#         topology_file_path = topology_file_path,
#         flows_file_target_path = flows_file_path
#     )

# def generate_policy():
#     policy_generator = p_gen.DestinationPolicyGenerator(
#         topology_file_path = topology_file_path,
#         flows_file_path = flows_file_path,
#         policy_file_target_path = policy_file_path
#     )

def prepare_parser():
    class Parser(object):
        
        class Packet(object):

            def __init__(self):
                self.protocols = []

            def __getitem__(self, item):
                return self.__getattribute__(item)

            def describe(self):
                print self.protocols

        def __init__(self, protocols_description_file_path):
            self.read_protocols(protocols_description_file_path)
            self.load_variables_and_fields()
            self.translate_next_protocols_fields()

        def read_protocols(self, protocols_description_file_path):
            with open(protocols_description_file_path, "r") as f:
                protocols_file = json.loads(f.read())
                self.protocols_used = protocols_file["protocols_used"]
                self.protocols_stack = protocols_file["protocols_stacks"]
                self.protocols_definition = protocols_file["protocols_definition"]
                self.next_protocols_fields = protocols_file["next_protocols_fields"]
                self.match_fields_used = protocols_file["match_fields_used"]
                self.match_fields_to_learn = protocols_file["match_fields_to_learn"] 

        def load_variables_and_fields(self):
            self.variables = {}
            self.fields = {}
            for protocol, definition in self.protocols_definition.items():
                for variable in definition.get("variables",[]):
                    parsed_variable = self.parse_variable(variable["value"])
                    self.variables[variable["name"]] = parsed_variable

                self.fields[protocol] = []
                for field in definition["fields"]:
                    self.fields[protocol].append((field["name"],field["size"]))

        def parse_variable(self,variable):
            try:
                variable = int(variable)
            except:
                pass
            try:
                variable = int(variable, base = 2)
            except:
                pass
            try:
                variable = int(variable, base = 16)
            except:
                pass
            return variable

        def translate_next_protocols_fields(self):
            self.next_protocol = {}
            for protocol, description in self.next_protocols_fields.items():
                next_field = description.get("next_protocol_field", None)
                if next_field is not None:
                    self.next_protocol[next_field] = {}
                    for next_protocol, value in description.get("next_protocol_value",{}).items():
                        value = self.variables.get(value, value)
                        self.next_protocol[next_field][value] = next_protocol

        def parse_packet(self, packet):
            parsed_packet = Parser.Packet()
            protocol = "Ethernet"
            still_parsing = True
            packet = to_bits(packet)
            while still_parsing:
                parsed_packet.protocols.append(protocol)
                parsed_packet.__setattr__(protocol, Parser.Packet())

                for field_name, field_size in self.fields[protocol]:
                    field_value = packet[0:field_size]
                    packet = packet[field_size:]
                    parsed_packet[protocol].__setattr__(field_name, field_value)
                
                still_parsing = False
                next_field = self.next_protocols_fields[protocol].get("next_protocol_field", None)
                if next_field is not None:
                    still_parsing = True
                    next_field_value = parsed_packet[protocol][next_field]
                    try:
                        protocol = self.next_protocol[next_field][int(next_field_value, 2)]
                    except:
                        still_parsing = False
                    
            return parsed_packet
            
    return Parser(protocols_description_file_path)


def start_mininet_network(topology):
    topology.generate_mininet_net()
    topology.generate_topology()
    topology.start()
    return topology
    
def to_bits(payload):
    # payload_bytes = []
    # for x in payload:
    #     payload_bytes.append(ord(x))
    # return payload_bytes
    return ''.join(format(ord(x), '08b') for x in payload)


def start_controller(topology, parser):
    switch = topology.node("sw")
    switch.initiate_communicator()
    switch.OSNetCommunicator.connect()
    switch.OSNetCommunicator.take_action("PrepareSwitch")

    endpoint = topology.node("EP_1")
    endpoint.initiate_communicator()
    endpoint.OSNetCommunicator.take_action("Command", command = "ip link set dev lo up")
    
    switch.OSNetCommunicator.take_action(
            "InsertTableEntry", 
            table_name = "MyIngress.Flow_classifier",
            match_fields = { "hdr.Ethernet.dstAddr": {"low": "a0:a1:a2:a3:a4:a5", "high":"a0:a1:a2:a3:a4:ff"} },
            action_name = "MyIngress.append_iFabric_header",
            action_params = {"flow_id" : 12, "node_id": 13},
            priority = 12)
    switch.OSNetCommunicator.get_state("TableEntries")
    while True:
        endpoint.OSNetCommunicator.take_action("Command", command = "python tester.py")
        packetin = switch.OSNetCommunicator.take_action("ReceivePacket")
        payload = packetin.packet.payload
        metadata = packetin.packet.metadata 
        for meta in metadata:
            metadata_id = meta.metadata_id 
            value = to_bits(meta.value)
        payload = parser.parse_packet(payload)
        payload.describe()
            
        

        

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clean', help='Stop previous mininet process and clean directories',
                        action='store_true', required=False, default=False)
    return parser.parse_args()

def clean_setup():
    os.system("sudo mn -c")
    os.system("rm -f *.pcap")
    os.system(" ".join(["rm -rf ", build_folder, pcaps_folder, logs_folder]))
    
if __name__ == "__main__":
    args = get_args()
    clean_setup()
    print 
    try:
        prepare_folders()
        topo = prepare_topology()
        parser = prepare_parser()
        # generate_flows()
        # generate_policy()
        started_topo = start_mininet_network(topo)
        start_controller(started_topo, parser)
    except Exception, err:
        print "Exception: ", err
        print 
        print traceback.print_exc()
    finally:
        clean_setup()
