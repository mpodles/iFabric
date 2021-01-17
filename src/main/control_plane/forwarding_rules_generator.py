import json

class ForwardingRules():
    def __init__(self, links, flows, policy):
        self.links = links
        self.flows = flows
        self.policy = policy
    
    def getRules(self):
        rules = {}
        for sw, _ in self.links.items():
            rules[sw] = self.get_rules_for_sw(sw)
        return rules
            
    def get_rules_for_sw(self, sw):
        rules_of_sw = []
        for flow_name, flow_id in self.flows.items():
            if flow_name == "Node_1_flow":
                rules_of_sw.append(self.get_rule_for_flow_for_sw(flow_id, sw))
        return rules_of_sw
    
    def get_rule_for_flow_for_sw(self, flow_id, sw):
        if "Leaf_1" in sw:
            rule = {
            "multicast_group_id" : flow_id,
            "replicas" : [
            {
                "egress_port" : 1,
                "instance" : 1
            }
            ]
        }

        if "Leaf_2" in sw:
            rule = {
            "multicast_group_id" : flow_id,
            "replicas" : [
            {
                "egress_port" : 2,
                "instance" : 2
            }
            ]
        }

        if "Spine" in sw:
            rule = {
            "multicast_group_id" : flow_id,
            "replicas" : [
            {
                "egress_port" : 2,
                "instance" : 2
            }
            ]
        }
            
        return rule
