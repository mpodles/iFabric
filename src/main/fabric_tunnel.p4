/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_MYTUNNEL = 0x1212;
const bit<16> TYPE_ETHERNET = 0x0001;
const bit<16> TYPE_IPV4 = 0x800;
const bit<32> MAX_TUNNEL_ID = 1 << 15;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<48> time_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header myTunnel_t {
    bit<16> header_type;
    bit<16> next_protocol;
    bit<16> flow_id;
    bit<16> node_id;
    bit<16> group_id;
}

header ipv4_t {
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

struct metadata {
    /* empty */
}

struct headers {
    myTunnel_t   myTunnel;
    ethernet_t   ethernet;
    ipv4_t       ipv4;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition select(packet.lookahead<myTunnel_t>().header_type) {
            TYPE_MYTUNNEL              : parse_myTunnel;
            default                    : parse_ethernet;
        }     
        //transition parse_ethernet;  
    }

    state parse_myTunnel {
        packet.extract(hdr.myTunnel);
        transition select(hdr.myTunnel.next_protocol) {
            TYPE_ETHERNET: parse_ethernet;
            default: accept;
        }
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    counter((MAX_TUNNEL_ID), CounterType.bytes) ingress_byte_cnt;
    
    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    action append_myTunnel_header(
        bit<16> flow_id,
        bit<16> node_id,
        bit<16> group_id) {
        hdr.myTunnel.setValid();
        hdr.myTunnel.header_type = TYPE_MYTUNNEL;
        hdr.myTunnel.next_protocol = TYPE_ETHERNET;
        hdr.myTunnel.flow_id = flow_id;
        hdr.myTunnel.node_id = node_id;
        hdr.myTunnel.group_id = group_id;
    }

    action fix_header(bit<16> flow_id){
        hdr.myTunnel.flow_id = flow_id;
    }

    table node_and_group_classifier {
        key = {
            standard_metadata.egress_port: exact;
        }
        actions = {
            append_myTunnel_header;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    table flow_classifier {
        key = {
            hdr.ipv4.dstAddr: exact;
            hdr.ethernet.dstAddr: range;
        }
        actions = {
            fix_header;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    apply {
        if (!hdr.myTunnel.isValid()) 
            flow_classifier.apply();          
        ingress_byte_cnt.count((bit<32>) hdr.myTunnel.flow_id);
        standard_metadata.mcast_grp = (bit<16>)hdr.myTunnel.flow_id;
        }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    counter((MAX_TUNNEL_ID), CounterType.bytes) egress_byte_cnt;

    action strip_header(){
        hdr.myTunnel.setInvalid();
    }
    
    table port_checker {
        key = {
            standard_metadata.egress_port: exact;
        }
        actions = {
            strip_header;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    apply {
        egress_byte_cnt.count((bit<32>) hdr.myTunnel.flow_id);
        port_checker.apply();       
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
	}
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.myTunnel);
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
