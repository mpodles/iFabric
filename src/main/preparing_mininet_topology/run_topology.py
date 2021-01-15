#!/usr/bin/env python2
# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Adapted by Robert MacDavid (macdavid@cs.princeton.edu) from scripts found in
# the p4app repository (https://github.com/p4lang/p4app)
#
# We encourage you to dissect this script to better understand the BMv2/Mininet
# environment used by the P4 tutorial.
#
import os, sys, json, subprocess, re, argparse
from time import sleep

from p4_mininet import P4Switch, P4Host, iFabricNode

from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI

from p4runtime_switch import P4RuntimeSwitch

def configureP4Switch(**switch_args):
    """ Helper class that is called by mininet to initialize
        the virtual P4 switches. The purpose is to ensure each
        switch's thrift server is using a unique port.
    """
    if "sw_path" in switch_args and 'grpc' in switch_args['sw_path']:
        # If grpc appears in the BMv2 switch target, we assume will start P4Runtime
        class ConfiguredP4RuntimeSwitch(P4RuntimeSwitch):
            def __init__(self, *opts, **kwargs):
                kwargs.update(switch_args)
                P4RuntimeSwitch.__init__(self, *opts, **kwargs)

            def describe(self):
                print "%s -> gRPC port: %d" % (self.name, self.grpc_port)

        return ConfiguredP4RuntimeSwitch
    else:
        class ConfiguredP4Switch(P4Switch):
            next_thrift_port = 9090
            def __init__(self, *opts, **kwargs):
                global next_thrift_port
                kwargs.update(switch_args)
                kwargs['thrift_port'] = ConfiguredP4Switch.next_thrift_port
                ConfiguredP4Switch.next_thrift_port += 1
                P4Switch.__init__(self, *opts, **kwargs)

            def describe(self):
                print "%s -> Thrift port: %d" % (self.name, self.thrift_port)

        return ConfiguredP4Switch


class ExerciseTopo(Topo):
    """ The mininet topology class for the P4 tutorial exercises.
    """
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
            self.addSwitch(sw, log_file="%s/%s.log" %(self.log_dir, sw), cls=switchClass)
    
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


class ExerciseRunner:
    """
        Attributes:
            log_dir  : string   // directory for mininet log files
            pcap_dir : string   // directory for mininet switch pcap files
            quiet    : bool     // determines if we print logger messages

            nodes    : dict<string, dict> // mininet nodes names and their associated properties
            switches : dict<string, dict> // mininet switch names and their associated properties
            links    : list<dict>         // list of mininet link properties

            switch_json : string // json of the compiled p4 example
            bmv2_exe    : string // name or path of the p4 switch binary

            topo : Topo object   // The mininet topology instance
            net : Mininet object // The mininet instance

    """
    def logger(self, *items):
        if not self.quiet:
            print(' '.join(items))

    def format_latency(self, l):
        """ Helper method for parsing link latencies from the topology json. """
        if isinstance(l, (str, unicode)):
            return l
        else:
            return str(l) + "ms"


    def __init__(self, topology_file_path, compiled_p4_path, logs_folder, pcaps_folder, bmv2_exe, quiet=False):
        """ Initializes some attributes and reads the topology json. Does not
            actually run the exercise. Use run_exercise() for that.

            Arguments:
                topo_file : string    // A json file which describes the exercise's
                                         mininet topology.
                log_dir  : string     // Path to a directory for storing exercise logs
                pcap_dir : string     // Ditto, but for mininet switch pcap files
                switch_json : string  // Path to a compiled p4 json for bmv2
                bmv2_exe    : string  // Path to the p4 behavioral binary
                quiet : bool          // Enable/disable script debug messages
        """

        topo_file = topology_file_path
        log_dir = logs_folder
        pcap_dir = pcaps_folder
        switch_json = compiled_p4_path
        bmv2_exe = bmv2_exe
        self.quiet = quiet
        self.logger('Reading topology file.')
        with open(topo_file, 'r') as f:
            topo = json.load(f)
        self.nodes = topo['nodes']
        self.switches = topo['switches']
        self.links = topo['links']
        self.node_links = topo['node_links']
        #self.links = self.parse_links(topo['links'])

        # Ensure all the needed directories exist and are directories
        for dir_name in [log_dir, pcap_dir]:
            if not os.path.isdir(dir_name):
                if os.path.exists(dir_name):
                    raise Exception("'%s' exists and is not a directory!" % dir_name)
                os.mkdir(dir_name)
        self.log_dir = log_dir
        self.pcap_dir = pcap_dir
        self.switch_json = switch_json
        self.bmv2_exe = bmv2_exe

    def parse_links(self, unparsed_links): #TODO: make topology file links already parsed
        """ Given a list of links descriptions of the form [node1, node2, latency, bandwidth]
            with the latency and bandwidth being optional, parses these descriptions
            into dictionaries and store them as self.links
        """
        links = []
        for link in unparsed_links:
            # make sure each link's endpoints are ordered alphabetically
            s, t, = link[0], link[1]
            if s > t:
                s,t = t,s

            link_dict = {'node1':s,
                        'node2':t,
                        'latency':'0ms',
                        'bandwidth':None
                        }
            if len(link) > 2:
                link_dict['latency'] = self.format_latency(link[2])
            if len(link) > 3:
                link_dict['bandwidth'] = link[3]

            if link_dict['node1'][0] == 'h':
                assert link_dict['node2'][0] == 's', 'Hosts should be connected to switches, not ' + str(link_dict['node2'])
            links.append(link_dict)
        return links


    def run_exercise(self):
        """ Sets up the mininet instance, programs the switches,
            and starts the mininet CLI. This is the main method to run after
            initializing the object.
        """
        # Initialize mininet with the topology specified by the config
        self.create_network()
        self.net.start()
        sleep(1)

        # some programming that must happen after the net has started
        self.program_nodes()

        self.prepare_switches_file()

        # wait for that to finish. Not sure how to do this better
        sleep(1)

        #self.simulate_traffic()

        self.do_net_cli()
        # stop right after the CLI is exited
        self.net.stop()


    def create_network(self):
        """ Create the mininet network object, and store it as self.net.

            Side effects:
                - Mininet topology instance stored as self.topo
                - Mininet instance stored as self.net
        """
        self.logger("Building mininet topology.")

        defaultSwitchClass = configureP4Switch(
                                sw_path=self.bmv2_exe,
                                json_path=self.switch_json,
                                log_console=True,
                                pcap_dump=self.pcap_dir)

        self.topo = ExerciseTopo(self.nodes, self.switches, self.links, self.node_links, self.log_dir, self.bmv2_exe, self.pcap_dir)

        self.net = Mininet(topo = self.topo,
                      link = TCLink,
                      host = iFabricNode,
                      switch = defaultSwitchClass,
                      controller = None)

    def program_nodes(self):
        """ Execute any commands provided in the topology.json file on each Mininet host
        """
        for node_name, node_info in self.nodes.items():
            h = self.net.get(node_name)
            if "commands" in node_info:
                for cmd in node_info["commands"]:
                    h.cmd(cmd)

    def prepare_switches_file(self):
        """ This method will use switches dictionary to prepare file 
        with device id and grpc ports for P4Runtime controller
        """
        result_dictionary = {}        
        for sw_name, sw_dict in self.switches.iteritems():
            result_dictionary[sw_name] = self.prepare_switch_dictionary(sw_name, sw_dict)
        result_string = json.dumps(result_dictionary)

        with open("./build/switches_vars.json", "w") as f:
            f.write(result_string)

    def prepare_switch_dictionary(self, sw_name, sw_dict):
        switch_dictionary = {}
        sw_obj = self.net.get(sw_name)
        grpc_port = sw_obj.grpc_port
        device_id = sw_obj.device_id
        runtime_json = sw_dict['runtime_json']
        switch_dictionary['grpc_port'] = grpc_port
        switch_dictionary['device_id'] = device_id
        switch_dictionary['runtime_json'] = runtime_json
        return switch_dictionary


    def program_switch_cli(self, sw_name, sw_dict):
        """ This method will start up the CLI and use the contents of the
            command files as input.
        """
        cli = 'simple_switch_CLI'
        # get the port for this particular switch's thrift server
        sw_obj = self.net.get(sw_name)
        thrift_port = sw_obj.thrift_port

        cli_input_commands = sw_dict['cli_input']
        self.logger('Configuring switch %s with file %s' % (sw_name, cli_input_commands))
        with open(cli_input_commands, 'r') as fin:
            cli_outfile = '%s/%s_cli_output.log'%(self.log_dir, sw_name)
            with open(cli_outfile, 'w') as fout:
                subprocess.Popen([cli, '--thrift-port', str(thrift_port)],
                                 stdin=fin, stdout=fout)

    # def program_switches(self):
    #     """ This method will program each switch using the BMv2 CLI and/or
    #         P4Runtime, depending if any command or runtime JSON files were
    #         provided for the switches.
    #     """
    #     for sw_name, sw_dict in self.switches.iteritems():
    #         if 'cli_input' in sw_dict:
    #             self.program_switch_cli(sw_name, sw_dict)
    #         if 'runtime_json' in sw_dict:
    #             self.program_switch_p4runtime(sw_name, sw_dict)



    def do_net_cli(self):
        """ Starts up the mininet CLI and prints some helpful output.

            Assumes:
                - A mininet instance is stored as self.net and self.net.start() has
                  been called.
        """
        for s in self.net.switches:
            s.describe()
        for h in self.net.hosts:
            h.describe()
        self.logger("Starting mininet CLI")
        # Generate a message that will be printed by the Mininet CLI to make
        # interacting with the simple switch a little easier.
        print('')
        print('======================================================================')
        print('Welcome to the BMV2 Mininet CLI!')
        print('======================================================================')
        print('Your P4 program is installed into the BMV2 software switch')
        print('and your initial runtime configuration is loaded. You can interact')
        print('with the network using the mininet CLI below.')
        print('')
        if self.switch_json:
            print('To inspect or change the switch configuration, connect to')
            print('its CLI from your host operating system using this command:')
            print('  simple_switch_CLI --thrift-port <switch thrift port>')
            print('')
        print('To view a switch log, run this command from your host OS:')
        print('  tail -f %s/<switchname>.log' %  self.log_dir)
        print('')
        print('To view the switch output pcap, check the pcap files in %s:' % self.pcap_dir)
        print(' for example run:  sudo tcpdump -xxx -r s1-eth1.pcap')
        print('')
        if 'grpc' in self.bmv2_exe:
            print('To view the P4Runtime requests sent to the switch, check the')
            print('corresponding txt file in %s:' % self.log_dir)
            print(' for example run:  cat %s/s1-p4runtime-requests.txt' % self.log_dir)
            print('')

        CLI(self.net)


def get_args():
    cwd = os.getcwd()
    default_logs = os.path.join(cwd, 'logs')
    default_pcaps = os.path.join(cwd, 'pcaps')
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', help='Suppress log messages.',
                        action='store_true', required=False, default=False)
    parser.add_argument('-t', '--topo', help='Path to topology json',
                        type=str, required=False, default='./topology.json')
    parser.add_argument('-l', '--log-dir', type=str, required=False, default=default_logs)
    parser.add_argument('-p', '--pcap-dir', type=str, required=False, default=default_pcaps)
    parser.add_argument('-j', '--switch_json', type=str, required=False)
    parser.add_argument('-b', '--behavioral-exe', help='Path to behavioral executable',
                                type=str, required=False, default='simple_switch')
    return parser.parse_args()



# if __name__ == '__main__':
#     # from mininet.log import setLogLevel
#     # setLogLevel("info")

#     args = get_args()
#     exercise = ExerciseRunner(args.topo, args.log_dir, args.pcap_dir,
#                               args.switch_json, args.behavioral_exe, args.quiet)

#     exercise.run_exercise()

