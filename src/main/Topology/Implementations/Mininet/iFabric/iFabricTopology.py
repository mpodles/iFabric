from Mininet import MininetTopology
from Mininet.Switches import Bmv2GrpcSwitch
import os

class iFabricTopology(MininetTopology):

    def __init__(self,files):
        MininetTopology.__init__(switch_class = iFabricSwitch, endpoint_class = iFabricEndPoint, link_class = iFabricLink)

        compiled_p4 =  files["compiled_p4"] #"./fabric_tunnel_compiled.json"

        if compiled_p4 is not None:
            # make sure that the provided JSON file exists
            if not os.path.isfile(compiled_p4):
                error("Invalid compiled P4 json file: {}\n".format(compiled_p4))
                exit(1)
            self.compiled_p4 = compiled_p4
        else:
            self.compiled_p4 = None