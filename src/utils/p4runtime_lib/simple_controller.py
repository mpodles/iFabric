#!/usr/bin/env python2
#
# Copyright 2017-present Open Networking Foundation
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
import argparse
import json
import timeit
import os
import sys
from time import sleep

import bmv2
import helper


def error(msg):
    print >> sys.stderr, ' - ERROR! ' + msg

def info(msg):
    print >> sys.stdout, ' - ' + msg


class ConfException(Exception):
    pass


# def main():
#     parser = argparse.ArgumentParser(description='P4Runtime Simple Controller')

#     parser.add_argument('-a', '--p4runtime-server-addr',
#                         help='address and port of the switch\'s P4Runtime server (e.g. 192.168.0.1:50051)',
#                         type=str, action="store", required=True)
#     parser.add_argument('-d', '--device-id',
#                         help='Internal device ID to use in P4Runtime messages',
#                         type=int, action="store", required=True)
#     parser.add_argument('-p', '--proto-dump-file',
#                         help='path to file where to dump protobuf messages sent to the switch',
#                         type=str, action="store", required=True)
#     parser.add_argument("-c", '--runtime-conf-file',
#                         help="path to input runtime configuration file (JSON)",
#                         type=str, action="store", required=True)

#     args = parser.parse_args()

#     if not os.path.exists(args.runtime_conf_file):
#         parser.error("File %s does not exist!" % args.runtime_conf_file)
#     workdir = os.path.dirname(os.path.abspath(args.runtime_conf_file))
#     with open(args.runtime_conf_file, 'r') as sw_conf_file:
#         program_switch(addr=args.p4runtime_server_addr,
#                        device_id=args.device_id,
#                        sw_conf_file=sw_conf_file,
#                        workdir=workdir,
#                        proto_dump_fpath=args.proto_dump_file)

class Controller():
    def __init__(self):
        self.project_directory = "/home/mpodles/iFabric/src/main/"
        self.connections = {}
        self.read_topology()
        self.read_flow_ids()
        self.read_policy()
  
    
    def read_topology(self):
        topo_file = self.project_directory + "sig-topo/topology.json"
        with open(topo_file, 'r') as f:
            topo = json.load(f)
            self.switches = topo['switches']
            self.groups = topo['groups']

        conf_file = self.project_directory + "build/switches_vars.json"
        with open(conf_file, 'r') as f:
            self.switches_config =  json.load(f)

    def read_flow_ids(self):
        flows_file = self.project_directory + "build/flow_ids.json"
        with open(flows_file, 'r') as f:
            self.flows = json.load(f)

    def read_policy(self):
        policy_file = self.project_directory + "sig-topo/policy.json"
        with open(policy_file, 'r') as f:
            self.policy = json.load(f)

    def program_switch_p4runtime(self, sw_name, sw_dict):
        """ This method will use P4Runtime to program the switch using the
            content of the runtime JSON file as input.
        """
        sw_conf = self.switches_config[sw_name]
        grpc_port = sw_conf["grpc_port"]
        device_id = sw_conf["device_id"]
        runtime_json = sw_dict['runtime_json']
        # self.logger('Configuring switch %s using P4Runtime with file %s' % (sw_name, runtime_json))
        with open(self.project_directory  + runtime_json, 'r') as sw_conf_file:
            outfile = self.project_directory + '/%s/%s-p4runtime-requests.txt' %("logs", sw_name)
            self.program_switch(
                sw_name = sw_name,
                addr='127.0.0.1:%d' % grpc_port,
                device_id=device_id,
                sw_conf_file=sw_conf_file,
                workdir=self.project_directory,
                proto_dump_fpath=outfile)

    def program_switches(self):
        """ This method will program each switch using the BMv2 CLI and/or
            P4Runtime, depending if any command or runtime JSON files were
            provided for the switches.
        """
        for sw_name, sw_dict in self.switches.iteritems():
                self.program_switch_p4runtime(sw_name, sw_dict)

    def check_switch_conf(self, sw_conf, workdir):
        required_keys = ["p4info"]
        files_to_check = ["p4info"]
        target_choices = ["bmv2"]

        if "target" not in sw_conf:
            raise ConfException("missing key 'target'")
        target = sw_conf['target']
        if target not in target_choices:
            raise ConfException("unknown target '%s'" % target)

        if target == 'bmv2':
            required_keys.append("bmv2_json")
            files_to_check.append("bmv2_json")

        for conf_key in required_keys:
            if conf_key not in sw_conf or len(sw_conf[conf_key]) == 0:
                raise ConfException("missing key '%s' or empty value" % conf_key)

        for conf_key in files_to_check:
            real_path = os.path.join(workdir, sw_conf[conf_key])
            if not os.path.exists(real_path):
                raise ConfException("file does not exist %s" % real_path)


    def program_switch(self, sw_name, addr, device_id, sw_conf_file, workdir, proto_dump_fpath):
        sw_conf = self.json_load_byteified(sw_conf_file)
        try:
            self.check_switch_conf(sw_conf=sw_conf, workdir=workdir)
        except ConfException as e:
            error("While parsing input runtime configuration: %s" % str(e))
            return

        info('Using P4Info file %s...' % sw_conf['p4info'])
        p4info_fpath = os.path.join(workdir, sw_conf['p4info'])
        self.p4info_helper = helper.P4InfoHelper(p4info_fpath)

        target = sw_conf['target']

        info("Connecting to P4Runtime server on %s (%s)..." % (addr, target))

        if target == "bmv2":
            sw = bmv2.Bmv2SwitchConnection(name=sw_name, address=addr, device_id=device_id,
                                        proto_dump_file=proto_dump_fpath)
            self.connections[sw_name] = sw
        else:
            raise Exception("Don't know how to connect to target %s" % target)

        sw.MasterArbitrationUpdate()

        if target == "bmv2":
            info("Setting pipeline config (%s)..." % sw_conf['bmv2_json'])
            bmv2_json_fpath = os.path.join(workdir, sw_conf['bmv2_json'])
            sw.SetForwardingPipelineConfig(p4info=self.p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_json_fpath)
        else:
            raise Exception("Should not be here")

        if 'table_entries' in sw_conf:
            table_entries = sw_conf['table_entries']
            info("Inserting %d table entries..." % len(table_entries))
            for entry in table_entries:
                info(self.tableEntryToString(entry))
                self.insertTableEntry(sw, entry)

        if 'multicast_group_entries' in sw_conf:
            group_entries = sw_conf['multicast_group_entries']
            info("Inserting %d group entries..." % len(group_entries))
            for entry in group_entries:
                info(self.groupEntryToString(entry))
                self.insertMulticastGroupEntry(sw, entry)

        if 'clone_session_entries' in sw_conf:
            clone_entries = sw_conf['clone_session_entries']
            info("Inserting %d clone entries..." % len(clone_entries))
            for entry in clone_entries:
                info(self.cloneEntryToString(entry))
                self.insertCloneGroupEntry(sw, entry)
        #     sw.shutdown()


    def insertTableEntry(self, sw, flow):
        table_name = flow['table']
        match_fields = flow.get('match') # None if not found
        action_name = flow['action_name']
        default_action = flow.get('default_action') # None if not found
        action_params = flow['action_params']
        priority = flow.get('priority')  # None if not found

        table_entry = self.p4info_helper.buildTableEntry(
            table_name=table_name,
            match_fields=match_fields,
            default_action=default_action,
            action_name=action_name,
            action_params=action_params,
            priority=priority)

        sw.WriteTableEntry(table_entry)
    
    def modifyTableEntry(self, sw, flow):
        table_name = flow['table']
        match_fields = flow.get('match') # None if not found
        action_name = flow['action_name']
        default_action = flow.get('default_action') # None if not found
        action_params = flow['action_params']
        priority = flow.get('priority')  # None if not found

        table_entry = self.p4info_helper.buildTableEntry(
            table_name=table_name,
            match_fields=match_fields,
            default_action=default_action,
            action_name=action_name,
            action_params=action_params,
            priority=priority)

        sw.WriteTableEntry(table_entry, modify=True)


    def printCounter(self, sw, counter_name, flow):
        """
        Reads the specified counter at the specified index from the switch. In our
        program, the index is the tunnel ID. If the index is 0, it will return all
        values from the counter.

        :param p4info_helper: the P4Info helper
        :param sw:  the switch connection
        :param counter_name: the name of the counter from the P4 program
        :param index: the counter index (in our case, the tunnel ID)
        """
        flow_name, index = flow
        for response in sw.ReadCounters(self.p4info_helper.get_counters_id(counter_name), int(index)):
            for entity in response.entities:
                counter = entity.counter_entry
                print "%s %s %s: %d packets (%d bytes)" % (
                    sw.name, counter_name, flow_name,
                    counter.data.packet_count, counter.data.byte_count
                )

    # object hook for josn library, use str instead of unicode object
    # https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-from-json
    def json_load_byteified(self, file_handle):
        return self._byteify(json.load(file_handle, object_hook=self._byteify),
                        ignore_dicts=True)


    def _byteify(self, data, ignore_dicts=False):
        # if this is a unicode string, return its string representation
        if isinstance(data, unicode):
            return data.encode('utf-8')
        # if this is a list of values, return list of byteified values
        if isinstance(data, list):
            return [self._byteify(item, ignore_dicts=True) for item in data]
        # if this is a dictionary, return dictionary of byteified keys and values
        # but only if we haven't already byteified it
        if isinstance(data, dict) and not ignore_dicts:
            return {
                self._byteify(key, ignore_dicts=True): self._byteify(value, ignore_dicts=True)
                for key, value in data.iteritems()
            }
        # if it's anything else, return it in its original form
        return data


    def tableEntryToString(self, flow):
        if 'match' in flow:
            match_str = ['%s=%s' % (match_name, str(flow['match'][match_name])) for match_name in
                        flow['match']]
            match_str = ', '.join(match_str)
        elif 'default_action' in flow and flow['default_action']:
            match_str = '(default action)'
        else:
            match_str = '(any)'
        params = ['%s=%s' % (param_name, str(flow['action_params'][param_name])) for param_name in
                flow['action_params']]
        params = ', '.join(params)
        return "%s: %s => %s(%s)" % (
            flow['table'], match_str, flow['action_name'], params)


    def groupEntryToString(self, rule):
        group_id = rule["multicast_group_id"]
        replicas = ['%d' % replica["egress_port"] for replica in rule['replicas']]
        ports_str = ', '.join(replicas)
        return 'Group {0} => ({1})'.format(group_id, ports_str)

    def cloneEntryToString(self, rule):
        clone_id = rule["clone_session_id"]
        if "packet_length_bytes" in rule:
            packet_length_bytes = str(rule["packet_length_bytes"])+"B"
        else:
            packet_length_bytes = "NO_TRUNCATION"
        replicas = ['%d' % replica["egress_port"] for replica in rule['replicas']]
        ports_str = ', '.join(replicas)
        return 'Clone Session {0} => ({1}) ({2})'.format(clone_id, ports_str, packet_length_bytes)

    def insertMulticastGroupEntry(self, sw, rule):
        mc_entry = self.p4info_helper.buildMulticastGroupEntry(rule["multicast_group_id"], rule['replicas'])
        sw.WritePREEntry(mc_entry)

    def modifyMulticastGroupEntry(self, sw, rule):
        mc_entry = self.p4info_helper.buildMulticastGroupEntry(rule["multicast_group_id"], rule['replicas'])
        sw.WritePREEntry(mc_entry, modify=True)

    def insertCloneGroupEntry(self, sw, rule):
        clone_entry = self.p4info_helper.buildCloneSessionEntry(rule['clone_session_id'], rule['replicas'],
                                                        rule.get('packet_length_bytes', 0))
        sw.WritePREEntry(clone_entry)

    def getState(self):
        for conn in self.connections.values():
            for flow in self.flows.items():
                self.getFlowState(conn, flow)

    def getFlowState(self, conn, flow):
        self.printCounter(conn, "MyIngress.ingress_byte_cnt", flow)
        self.printCounter(conn, "MyEgress.egress_byte_cnt", flow)

    def readTableRules(self, sw):
        """
        Reads the table entries from all tables on the switch.

        :param p4info_helper: the P4Info helper
        :param sw: the switch connection
        """
            
        print '\n----- Reading tables rules for %s -----' % sw.name
        for response in sw.ReadTableEntries():
            for entity in response.entities:
                entry = entity.table_entry
                # TODO For extra credit, you can use the p4info_helper to translate
                #      the IDs in the entry to names
                table_name = self.p4info_helper.get_tables_name(entry.table_id)
                print '%s: ' % table_name,
                for m in entry.match:
                    print self.p4info_helper.get_match_field_name(table_name, m.field_id),
                    print '%r' % (self.p4info_helper.get_match_field_value(m),),
                action = entry.action.action
                action_name = self.p4info_helper.get_actions_name(action.action_id)
                print '->', action_name,
                for p in action.params:
                    print self.p4info_helper.get_action_param_name(action_name, p.param_id),
                    print '%r' % p.value,
                print

    def writeForwardingRules(self,sw):
        flow = "flow1"
        rule = self.getTestRules(sw, flow)
        self.modifyMulticastGroupEntry(controller.connections[sw], rule)

    def getTestRules(self, sw, flow):
        flow_id = self.flows[flow]
        if sw == "s1":
            rule = {
        "multicast_group_id" : flow_id,
        "replicas" : [
          {
            "egress_port" : 2,
            "instance" : 2
          },
          {
            "egress_port" : 4,
            "instance" : 4
          }
        ]
      }
        elif sw == "s2":
            rule = {
        "multicast_group_id" : flow_id,
        "replicas" : [
          {
            "egress_port" : 48,
            "instance" : 48
          },
          {
            "egress_port" : 4,
            "instance" : 4
          }
        ]
      }
        elif sw == "s3":
            rule = {
        "multicast_group_id" : flow_id,
        "replicas" : [
          {
            "egress_port" : 48,
            "instance" : 48
          }
        ]
      }
        elif sw == "s4":
            rule = {
        "multicast_group_id" : flow_id,
        "replicas" : [
          {
            "egress_port" : 48,
            "instance" : 48
          }
        ]
      }
        return rule


if __name__ == '__main__':
    # main()
    controller = Controller()
    controller.program_switches()
    # start = timeit.timeit()
    # controller.getAllCounters()
    # end = timeit.timeit()
    # print(end - start)

    print "Switches programmed"
    for i in range (1,5):
        sw = "s" + str(i)
        controller.readTableRules(controller.connections[sw])
        #controller.writeForwardingRules(sw)


    # while True:
    #     sleep(15)
    #     controller.getState()
    # print 
    # print "all rules read"
    # start = timeit.timeit()
    # flow = {
    #     "table": "MyIngress.myTunnel_operate",
    #     "match": {
    #       "hdr.myTunnel.flow_id": 1
    #     },
    #     "action_name": "MyIngress.assign_multicast",
    #     "action_params": {
    #       "multicast_group": 2
    #     }
    #   }
    # controller.modifyTableEntry(controller.connections["s1"], flow)
    # end = timeit.timeit()
    # print(end - start)
    # controller.readTableRules(controller.connections["s1"])
    # print controller.flows
    # print controller.policy
    # print controller.groups
    # rule = {
    #     "multicast_group_id" : 1,
    #     "replicas" : [
    #       {
    #         "egress_port" : 3,
    #         "instance" : 1
    #       },
    #       {
    #         "egress_port" : 4,
    #         "instance" : 1
    #       }
    #     ]
    #   }
    # controller.modifyMulticastGroupEntry(controller.connections["s1"], rule)


    
