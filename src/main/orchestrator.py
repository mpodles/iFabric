import os
import json
import argparse
import preparing_mininet_topology.construct_p4 as c_p4
import preparing_mininet_topology.run_topology as r_topo

main_project_directory = os.path.dirname(__file__)
with open(os.path.join(main_project_directory, "folders_and_files.json"), "r") as structure_file:
    structure = json.loads(structure_file.read())
print structure

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clean', help='Stop previous mininet process and clean directories',
                        action='store_true', required=False, default=False)
    return parser.parse_args()

def parse_structure():
    with open(os.path.join(main_project_directory, "folders_and_files.json"), "r") as structure_file:
        structure = json.loads(structure_file.read())
    return structure

def run_basic_pipeline():
    os.system("mkdir -p build logs pcap")
    # p4_constructor =  c_p4.P4Constructor()
    # os.system("$(P4C) --p4v 16 --p4runtime-files $(BUILD_DIR)/fabric_tunnel.p4.p4info.txt -o $(BUILD_DIR)/fabric_tunnel.json $(BUILD_DIR)/fabric_tunnel.p4")

    # exercise = r_topo.ExerciseRunner(args.topo, args.log_dir, args.pcap_dir,
    #                           args.switch_json, args.behavioral_exe, args.quiet)

    # exercise.run_exercise()

    
if __name__ == "__main__":
    args = get_args()

    structure = parse_structure()

    build_folder = structure["build_folder"]
    pcaps_folder = structure["pcaps_folder"]
    logs_folder = structure["logs_folder"]
    topology_file = structure["topology_file"]

    if args.clean:
        os.system("sudo mn -c")
        os.system("rm -f *.pcap")
        os.system(" ".join(["rm -rf ", build_folder, pcaps_folder, logs_folder]))
    else:
        run_basic_pipeline()
