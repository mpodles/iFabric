#!/usr/bin/env python
import sys
import struct
import os

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr
from scapy.layers.inet import Packet, IPOption
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.layers.inet import IP, TCP, UDP, Raw
from scapy.layers.inet import _IPOption_HDR

def handle_pkt(pkt):
    print "got a packet"
    pkt.show2()
    sys.stdout.flush()

def sniff_for_packet(communicator, interface):
    sys.stdout.flush()
    sniff(iface = interface,
          prn = lambda x: handle_pkt(x))
def perform_action(action, communicator, **params):
    sniff_for_packet(communicator, **params)
def get_function():
    return perform_action
