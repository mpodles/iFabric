import os
import json
import argparse
import timeit
import preparing_mininet_topology.construct_p4 as c_p4
import preparing_mininet_topology.run_topology as r_topo
import preparing_mininet_topology.prepare_topology_file as p_topo
import preparing_mininet_topology.configure_sample_flows as f_gen
import control_plane.simple_controller as contr
from time import sleep

#TODO: this file already needs refactoring

def parse_structure():
    with open(os.path.join(main_project_directory, "folders_and_files.json"), "r") as structure_file:
        structure = json.loads(structure_file.read())
    return structure

main_project_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(main_project_directory)

global exercise #TODO: do this some other way
structure = parse_structure()

build_folder = structure["build_folder"]
pcaps_folder = structure["pcaps_folder"]
logs_folder = structure["logs_folder"]
topology_file = structure["topology_file"]
p4_file_name = structure["p4_file_name"]
p4runtime_file_name = structure["p4runtime_file_name"]
compiled_p4_file_name = structure["compiled_p4_file_name"]
p4template = structure["p4template"]
configuration_folder = structure["configuration_folder"]
topology_description_file = structure["topology_description_file"]
protocols_folder = structure["protocols_folder"]
flows_file = structure["flows_file"]
flow_ids_file = structure["flow_ids_file"]
bmv2_exe = structure["BMV2_SWITCH_EXE"]

topology_file_path = os.path.join(main_project_directory, build_folder, topology_file)
p4_target_file_path = os.path.join(main_project_directory, build_folder, p4_file_name)
p4runtime_target_file_path = os.path.join(main_project_directory, build_folder, p4runtime_file_name)
compiled_p4_path = os.path.join(build_folder, compiled_p4_file_name)
configuration_folder_path =  os.path.join(main_project_directory, configuration_folder)
protocols_folder_path = os.path.join(main_project_directory, protocols_folder)
template_file_path =  os.path.join(main_project_directory, configuration_folder, p4template)
flows_file_path =  os.path.join(main_project_directory, configuration_folder, flows_file)
runtimes_files_path = os.path.join(main_project_directory, build_folder)
flow_ids_file_path = os.path.join(main_project_directory, build_folder, flow_ids_file)    

def prepare_folders():
    os.system("mkdir -p build logs pcap")

def prepare_topology():
    topology_configuration_path = os.path.join(main_project_directory, configuration_folder, topology_description_file)
    topology_target_path = os.path.join(main_project_directory, build_folder, topology_file)
    with open(topology_configuration_path, "r") as f:
        topo_config = json.loads(f.read())
    topology = p_topo.SpineLeaf(topo_config, topology_target_path)
    

def construct_p4_program():   
    p4_constructor =  c_p4.P4Constructor(
        topology_file_path = topology_file_path,
        protocols_folder_path = protocols_folder_path,
        configuration_folder_path = configuration_folder_path,
        flows_file_path = flows_file_path,
        template_file_path = template_file_path,
        p4_target_file_path = p4_target_file_path,
        runtimes_files_path = runtimes_files_path,
        flow_ids_file_path = flow_ids_file_path
        )

def compile_p4_program():
    cmd = "p4c-bm2-ss \
        --p4v 16 \
        --p4runtime-files "+ p4runtime_target_file_path +\
        " -o "+ compiled_p4_path +\
        " " + p4_target_file_path
    os.system(cmd)
    
def generate_flows():
    flows_generator = f_gen.DestinationFlowGenerator(
        topology_file_path = topology_file_path
    )

def run_basic_pipeline():
    global exercise
    exercise = r_topo.ExerciseRunner(topology_file_path, compiled_p4_path, logs_folder, pcaps_folder, bmv2_exe)
    exercise.run_exercise()
    exercise.net.stop()

def start_controller():
    controller = contr.Controller()
    controller.program_switches()
    # start = timeit.timeit()
    # controller.getAllCounters()
    # end = timeit.timeit()
    # print(end - start)
    print "Switches programmed"
    for i in range (1,5):
        sw = "s" + str(i)
        # controller.readTableRules(controller.connections[sw])
        controller.writeForwardingRules(sw)
    while True:
        sleep(4)
        controller.printCounter('s1', "MyIngress.ingress_byte_cnt", 'flow1', 48)


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
        # prepare_folders()
        # prepare_topology()
        # construct_p4_program()
        # compile_p4_program()
        generate_flows()
        # run_basic_pipeline()
        # start_controller()
