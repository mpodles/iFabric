from scapy.all import Packet
from scapy.fields import *
from scapy.layers.inet import Ether, IP, UDP, TCP
from scapy.all import sendp, send, get_if_list


class iFabric(Packet):
    name = 'iFabric'
    fields_desc = [
        ByteField("protocol",1)
    ]

ifaces = get_if_list()
fabric = iFabric()
pkt =  Ether(src='45:45:45:45:45:47', dst='45:45:45:45:45:46')
pkt =  pkt /IP(dst="1.1.1.1", src= "2.2.2.2") / TCP(dport=1234, sport=55123) 
for iface in ifaces:
    if iface != "lo":
        sendp(pkt, iface=iface, verbose=False)