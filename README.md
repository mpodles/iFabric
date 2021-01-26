# iFabric

This repo begins as a clone from https://github.com/p4lang/tutorials

Networking SDN Fabric that I would like to be a step towards fully automated telecommunications. 

The following document goes as follows:
  1. Current idea
  2. What's implemented
  3. Possible problems
  4. Possible extensions

## The idea
The idea consist of:
  1. Topology: any topology made out of P4 switches with SDN controller/s
  2. Configuration: things that Operator has to provide to the iFabric
  3. Control-plane: self-learning control-plane program
  
The iFabric should provide a abstract definition of any high-performance hardware network (Infrastracture as a Code). It should, under configuration that iFabric Operator makes, be capable of representing currently used networks (TCP/IP, Fibre Channel etc.) and any other packet-based networks that Operator might want to set-up to meet communication requirements.

The first requirement was set to try to be as backwards-compatible as possible.

The structures that make the iFabric are presented with provided example of how iFabric might implement IP/MAC network. Later, I highlight other sample iFabric network implementation.

## 1. Topology:

Topology is made out of P4 switch and Nodes connected to them. Both switch-interconnections and Nodes to switches are whatever we want. For Node it means that, they can be connected to any switchport on any swich with as many links per switch as they need. 

Nodes we might have in our first example could be:
  - email_server
  - database_server
  - firewall
  - website_1
  - website_dr_1
  - website_dr_2
  
Nodes can be put into Groups. We should be able to put Node into many groups at once for example:
  1. Websites:
    - website_1
    - website_dr_1
    - website_dr_2
  2. DR:
    - website_dr_1
    - website_dr_2
  3. Servers:
    - email_server
    - database_server

## 2. Configauration:

Before iFabric bringup (and possibly while fabric is operational, but unsure if current design supports that) we define:
  - flows, ( F = {flow_1, flow_2 ... flow_n} )
  - policy, ( Pol = {pol_1, pol_2 ... pol_3} )

Both of those should be as user-friendly and automated in their generation as possible.

Flows in an example IP/MAC fabric we might want to configure could look like:
F = {flow_to_firewall_ip, flow_to_server1, flow_to_servers_1_to_20 ...}

Policies we could define in this fabric could be:

Pol = {}

#### Flow - definition:
Named Set of Protocol Fields: ProtF_Set = {ProtF_1, ..., ProtF_n}, and set of ranges for protocol fields: ProtF_Ranges(ProtF_x) = {(ProtF_Low1, ProtF_High1), (ProtF_Low2, ProtF_High2) ... (ProtF_LowN, ProtF_HighN)} for ProtF_x from ProtF_Set



Protocol Field is any data that we can define using P4. For our IP/MAC fabric we could go with:
```
typedef bit<48> macAddr_t;

header Ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}


typedef bit<32> ip4Addr_t;

header IPv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}
```
In this example Protocol Fields we could use would f.g. be IPv4.dstAddr and Ethernet.dstAddr.
Ranges we could define as f.g. ProtF_Ranges(IPv4.dstAddr) = { (10.0.0.1, 10.0.0.26) }

Flows in this network could look like:
F = {flow_to_firewall_ip, flow_to_server1 , flow_to_servers_1_to_20 ...}

And they could look like:
flow_to_firewall_ip = {protocol: IPv4_
  
But we could go with something like:
```
typedef bit<256> server_ID;

header MyServerFarm_t {
    server_ID   dstID;
    server_ID   srcID;
    bit<32>   someServerPolicyField;
    bit<32>   processOnDstServerThatNeedsThisData;
}

```

And assume that host from their NICs send data with this header instead of whole TCP/IP stack. We can use as many headers/protocols (as hardware allows). They can be new or old ones combined in any way. (at least i assume that all P4 targets support that by default, which I believe they do)


Prot_Low and Prot_High are bit values that determine the span of values that we look at in the protocol.

Each flow also needs a priority that determines what happens if ranges from the flows overlaps.



#### Policy - definition
