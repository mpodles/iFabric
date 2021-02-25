import os
import json
import argparse
import timeit
from time import sleep
import threading
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/iFabric/TopologiesGenerator/TopologyGenerator.py')
from TopologyGenerator import SingleSwitchTopologyGenerator
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Implementations/Mininet/iFabric/iFabricTopology.py')
from iFabricTopology import iFabricTopology

main_project_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(main_project_directory)

structure = parse_structure()
def parse_structure():
    with open(os.path.join(main_project_directory, "folders_and_files.json"), "r") as structure_file:
        structure = json.loads(structure_file.read())
    return structure

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


topology_file_path = os.path.join(main_project_directory, build_folder, topology_file)
topology_description_file_path = os.path.join(main_project_directory, configuration_folder, topology_description_file)
logs_path = os.path.join(main_project_directory, logs_folder)
p4_code_file_path = os.path.join(main_project_directory, build_folder, p4_file_name)
p4runtime_info_file_path = os.path.join(main_project_directory, build_folder, p4runtime_file_name)
p4_json_file_path = os.path.join(main_project_directory, build_folder, compiled_p4_file_name)
configuration_folder_path =  os.path.join(main_project_directory, configuration_folder)
protocols_folder_path = os.path.join(main_project_directory, configuration_folder, protocols_folder)
protocols_description_file_path = os.path.join(main_project_directory, configuration_folder, protocols_description_file_name)
p4_template_file_path =  os.path.join(main_project_directory, configuration_folder, p4template)
flows_file_path =  os.path.join(main_project_directory, build_folder, flows_file)
runtimes_files_path = os.path.join(main_project_directory, build_folder)
flows_ids_file_path = os.path.join(main_project_directory, build_folder, flows_ids_file)  
policy_file_path = os.path.join(main_project_directory, build_folder, policy_file)
switches_connections_file_path = os.path.join(main_project_directory, build_folder, switches_connections_file)

def prepare_folders():
    os.system(" ".join(["mkdir -p", build_folder, pcaps_folder, logs_folder]))

def prepare_topology():
    sstg = SingleSwitchTopologyGenerator(
        topology_description_file_path = topology_description_file_path
    )
    sstg.generate_topology()
    topology = iFabricTopology(
        switches = sstg.switches,
        endpoints = sstg.endpoints,
        links = sstg.links,
        p4_template_file_path = p4_template_file_path,
        p4_code_file_path = p4_code_file_path,
        protocols_description_file_path = protocols_description_file_path,
        protocols_folder_path = protocols_folder_path,
        p4runtime_info_file_path = p4runtime_info_file_path, 
        p4_json_file_path = p4_json_file_path,
        log_dir = logs_folder, 
        pcap_dir = pcaps_folder
    )
        
    

# def construct_p4_program():   
#     p4_constructor =  c_p4.P4Constructor(
#         topology_file_path = topology_file_path,
#         protocols_folder_path = protocols_folder_path,
#         configuration_folder_path = configuration_folder_path,
#         flows_file_path = flows_file_path,
#         template_file_path = template_file_path,
#         p4_target_file_path = p4_target_file_path,
#         runtimes_files_path = runtimes_files_path,
#         flows_ids_file_path = flows_ids_file_path,
#         compiled_p4_file_path = compiled_p4_file_path,
#         p4runtime_target_file_path = p4runtime_target_file_path,
#         )

# def compile_p4_program():
#     cmd = "p4c-bm2-ss \
#         --p4v 16 \
#         --p4runtime-files "+ p4runtime_target_file_path +\
#         " -o "+ compiled_p4_file_path +\
#         " " + p4_target_file_path
#     os.system(cmd)
    
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

# def start_mininet_network():
#     topology.start_topology()
#     # global exercise
#     # exercise = r_topo.ExerciseRunner(
#     #     topology_file_path = topology_file_path,
#     #     logs_folder = logs_folder,
#     #     pcaps_folder = pcaps_folder,
#     #     compiled_p4_file_path = compiled_p4_file_path,
#     #     bmv2_exe = bmv2_exe
#     # )
#     # exercise.run_exercise()

# def start_controller():
#     print "Programming switches"
#     controller = contr.Controller(
#         topology_file_path = topology_file_path,
#         flows_ids_file_path = flows_ids_file_path,
#         switches_connections_file_path = switches_connections_file_path,
#         policy_file_path = policy_file_path,
#         runtimes_files_path = runtimes_files_path,
#         logs_path= logs_path
#     )
#     controller.start_state_gathering()

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
        prepare_topology()
        # generate_flows()
        # generate_policy()
        # construct_p4_program()
        # compile_p4_program()
        # start_mininet_network()
        # start_controller()
    except Exception as e:
        print "Exception: ", e
        print 
    finally:
        clean_setup()
