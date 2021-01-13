import os
import json
import argparse
import preparing_mininet_topology.construct_p4
import preparing_mininet_topology.configure_sample_flows

main_project_directory = os.path.dirname(__file__)
with open(os.path.join(main_project_directory, "folders_and_files.json"), "r") as structure_file:
    structure = json.loads(structure_file.read())
print structure

def get_args():
    # cwd = os.getcwd()
    # default_logs = os.path.join(cwd, 'logs')
    # default_pcaps = os.path.join(cwd, 'pcaps')
    parser = argparse.ArgumentParser()
    # parser.add_argument('-q', '--quiet', help='Suppress log messages.',
    #                     action='store_true', required=False, default=False)
    # parser.add_argument('-t', '--topo', help='Path to topology json',
    #                     type=str, required=False, default='./topology.json')
    parser.add_argument('-c', '--clean', help='Stop previous mininet process and clean directories',
                        action='store_true', required=False, default=False)
    # parser.add_argument('-l', '--log-dir', type=str, required=False, default=default_logs)
    # parser.add_argument('-p', '--pcap-dir', type=str, required=False, default=default_pcaps)
    # parser.add_argument('-j', '--switch_json', type=str, required=False)
    # parser.add_argument('-b', '--behavioral-exe', help='Path to behavioral executable',
    #                             type=str, required=False, default='simple_switch')
    return parser.parse_args()

def run_basic_pipeline():
    os.system("mkdir -p build logs pcap")
    p4_constructor =  construct_p4.P4Constructor()
    os.system("$(P4C) --p4v 16 --p4runtime-files $(BUILD_DIR)/fabric_tunnel.p4.p4info.txt -o $(BUILD_DIR)/fabric_tunnel.json $(BUILD_DIR)/fabric_tunnel.p4")
    

sudo python $(RUN_SCRIPT) -t $(TOPO) $(run_args)



if 
stop:
	sudo mn -c
	




clean: stop
	rm -f *.pcap
	rm -rf $(BUILD_DIR) $(PCAP_DIR) $(LOG_DIR)