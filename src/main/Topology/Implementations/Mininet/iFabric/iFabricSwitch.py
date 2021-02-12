from mininet.net import Mininet
from mininet.node import Switch, Host
from mininet.moduledeps import pathCheck
from mininet.log import info, error, debug
import tempfile
from time import sleep
import psutil
import os

class iFabricSwitch(Bmv2GrpcSwitch):
    def __init__(self, switch):
        Bmv2GrpcSwitch.__init__(self, switch)
        self.compiled_program = "iFabric"
