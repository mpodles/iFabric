/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_MYTUNNEL = 0x1212;
const bit<32> MAX_TUNNEL_ID = 1 << 15;
const bit<16> myTunnel_next_protocol_TYPE_ETHERNET = 0x0001;


/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

header myTunnel_t {
    bit<16> header_type;
    bit<16> next_protocol;
    bit<16> flow_id;
    bit<16> node_id;
    bit<16> group_id;
}

const bit<16> Ethernet_etherType_TYPE_IPv4 = 0x800;

typedef bit<48> macAddr_t;

header Ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}  
const bit<8>  IPv4_protocol_TYPE_TCP  = 6;

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
header TCP_t{
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<4>  res;
    bit<1>  cwr;
    bit<1>  ece;
    bit<1>  urg;
    bit<1>  ack;
    bit<1>  psh;
    bit<1>  rst;
    bit<1>  syn;
    bit<1>  fin;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}  


struct metadata {
    bit<16>    priority;
}

struct headers {
    myTunnel_t   myTunnel;
    Ethernet_t  Ethernet;  
    IPv4_t  IPv4;  
    TCP_t  TCP;  
    
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
            default                    : parse_Ethernet;
        }     
    }


    state parse_myTunnel {
        packet.extract(hdr.myTunnel);
        transition select(hdr.myTunnel.next_protocol) {
            myTunnel_next_protocol_TYPE_ETHERNET: parse_Ethernet;
            default: accept;
        }
    }

    state parse_Ethernet {
        packet.extract(hdr.Ethernet);
        
        transition select(hdr.Ethernet.etherType) {
            Ethernet_etherType_TYPE_IPv4: parse_IPv4;
            default: accept;
        }
    }
    state parse_IPv4 {
        packet.extract(hdr.IPv4);
        
        transition select(hdr.IPv4.protocol) {
            IPv4_protocol_TYPE_TCP: parse_TCP;
            default: accept;
        }
    }
    state parse_TCP {
        packet.extract(hdr.TCP);
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
        meta.priority = 0;
        hdr.myTunnel.setValid();
        hdr.myTunnel.header_type = TYPE_MYTUNNEL;
        hdr.myTunnel.next_protocol = myTunnel_next_protocol_TYPE_ETHERNET;
        hdr.myTunnel.flow_id = flow_id;
        hdr.myTunnel.node_id = node_id;
        hdr.myTunnel.group_id = group_id;
    }

    action fix_header(bit<16> flow_id, bit<16> priority){
        if (priority > meta.priority){
            hdr.myTunnel.flow_id = flow_id;
            meta.priority = priority;
        }
        
    }


    table IPv4_dstAddr_classifier {
        key = {
            hdr.IPv4.dstAddr: range;
        }
        actions = {
            fix_header;  
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }
    table Node_classifier {
        key = {
            standard_metadata.ingress_port: range;
        }
        actions = {
            append_myTunnel_header;  
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }
    table Ethernet_dstAddr_classifier {
        key = {
            hdr.Ethernet.dstAddr: range;
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
        if (!hdr.myTunnel.isValid()){
            Node_classifier.apply();
            IPv4_dstAddr_classifier.apply();Ethernet_dstAddr_classifier.apply();
        }         
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
            standard_metadata.egress_port: range;
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
        packet.emit(hdr.Ethernet);
        packet.emit(hdr.IPv4);
        packet.emit(hdr.TCP);
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