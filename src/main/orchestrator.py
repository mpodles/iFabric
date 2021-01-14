import os
import json
import argparse
import preparing_mininet_topology.construct_p4 as c_p4
import preparing_mininet_topology.run_topology as r_topo
import preparing_mininet_topology.prepare_topology_file as p_topo

def parse_structure():
    with open(os.path.join(main_project_directory, "folders_and_files.json"), "r") as structure_file:
        structure = json.loads(structure_file.read())
    return structure

main_project_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(main_project_directory)


structure = parse_structure()

build_folder = structure["build_folder"]
pcaps_folder = structure["pcaps_folder"]
logs_folder = structure["logs_folder"]
topology_file = structure["topology_file"]
p4_target_file = structure["p4target"]
configuration_folder = structure["configuration_folder"]
topology_description_file = structure["topology_description_file"]
protocols_folder = structure["protocols_folder"]

def prepare_folders():
    os.system("mkdir -p build logs pcap")

def generate_absolute_file_paths():
    #TODO: first generate all required file paths based on main_project_directory and structure dict
    pass

def prepare_topology():
    topology_configuration_path = os.path.join(main_project_directory, configuration_folder, topology_description_file)
    topology_target_path = os.path.join(main_project_directory, build_folder, topology_file)
    with open(topology_configuration_path, "r") as f:
        topo_config = json.loads(f.read())
    topology = p_topo.SpineLeaf(topo_config, topology_target_path)
    

def construct_p4_program():
    build_folder_path = os.path.join(main_project_directory, build_folder)
    topology_file_path = os.path.join(main_project_directory, build_folder, topology_file)
    configuration_folder_path =  os.path.join(main_project_directory, configuration_folder)
    p4_target_file_path = os.path.join(main_project_directory, build_folder, p4_target_file+".p4")
    protocols_folder_path = os.path.join(main_project_directory, protocols_folder)
    p4_constructor =  c_p4.P4Constructor(build_folder_path, topology_file_path, configuration_folder_path, p4_target_file_path, protocols_folder_path)

def compile_p4_program():
    os.system("p4c-bm2-ss --p4v 16 --p4runtime-files "+ build_folder +"/"+ p4_target_file +".p4.p4info.txt -o "+ build_folder +"/"+p4_target_file+".json "+build_folder+"/"+ p4_target_file )
    

def run_basic_pipeline():
    exercise = r_topo.ExerciseRunner(structure)
    exercise.run_exercise()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clean', help='Stop previous mininet process and clean directories',
                        action='store_true', required=False, default=False)
    return parser.parse_args()
    
if __name__ == "__main__":
    args = get_args()
    if args.clean:
        os.system("sudo mn -c")
        os.system("rm -f *.pcap")
        os.system(" ".join(["rm -rf ", build_folder, pcaps_folder, logs_folder]))
    else:
        prepare_folders()
        prepare_topology()
        construct_p4_program()
        compile_p4_program()
        run_basic_pipeline()
