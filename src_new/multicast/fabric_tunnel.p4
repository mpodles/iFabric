/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_MYTUNNEL = 0x1212;
const bit<16> TYPE_ETHERNET = 0x0001;
const bit<16> TYPE_IPV4 = 0x800;
const bit<32> MAX_TUNNEL_ID = 1 << 16;

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
    bit<32> flow_id;
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
    // remember the time of the last probe
    // counter<time_t>(MAX_TUNNEL_ID) ingress_last_time_reg;

    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    // action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
    //     standard_metadata.egress_spec = port;
    //     hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
    //     hdr.ethernet.dstAddr = dstAddr;
    //     hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    //}

    action append_myTunnel_header(
        bit<32> flow_id,
        bit<16> node_id,
        bit<16> group_id) {
        hdr.myTunnel.setValid();
        hdr.myTunnel.header_type = TYPE_MYTUNNEL;
        hdr.myTunnel.next_protocol = TYPE_ETHERNET;
        hdr.myTunnel.flow_id = flow_id;
        hdr.myTunnel.node_id = node_id;
        hdr.myTunnel.group_id = group_id;
    }

    action assign_multicast(bit<16> multicast_group){
        standard_metadata.mcast_grp = multicast_group;
    }
    

    // action myTunnel_forward(egressSpec_t port) {
    //     standard_metadata.egress_spec = port;
    //}

    // action myTunnel_egress(macAddr_t dstAddr, egressSpec_t port) {
    //     standard_metadata.egress_spec = port;
    //     hdr.ethernet.dstAddr = dstAddr;
    //     hdr.ethernet.etherType = hdr.myTunnel.proto_id;
    //     hdr.myTunnel.setInvalid();
    //     egressTunnelCounter.count((bit<32>) hdr.myTunnel.dst_id);
    // }

    table flow_classifier {
        key = {
            hdr.ipv4.dstAddr: exact;
        }
        actions = {
            append_myTunnel_header;
            assign_multicast;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = append_myTunnel_header(MAX_TUNNEL_ID, 404, 404);
    }

    // table ipv4_lpm {
    //     key = {
    //         hdr.ipv4.dstAddr: lpm;
    //     }
    //     actions = {
    //         ipv4_forward;
    //         myTunnel_ingress;
    //         drop;
    //         NoAction;
    //     }
    //     size = 1024;
    //     default_action = NoAction();
    // }

    table myTunnel_operate {
        key = {
            hdr.myTunnel.flow_id: exact;
        }
        actions = {
            assign_multicast;
            drop;
        }
        size = 1024;
        default_action = drop();
    }

    apply {
        if (!hdr.myTunnel.isValid()) {
            // Process only non-tunneled IPv4 packets.
            flow_classifier.apply();
            ingress_byte_cnt.count((bit<32>) hdr.myTunnel.flow_id);
        // bit<32> byte_cnt;
        // bit<32> new_byte_cnt;
        // time_t last_time;
        // time_t cur_time = standard_metadata.ingress_global_timestamp;
        // increment byte cnt for this packet's port
        // ingress_byte_cnt_reg.read(byte_cnt, (bit<32>)hdr.myTunnel.flow_id);
        // new_byte_cnt = byte_cnt + standard_metadata.packet_length;
        // reset the byte count when a probe packet passes through
        // ingress_byte_cnt_reg.write((bit<32>)hdr.myTunnel.flow_id, new_byte_cnt);
        // ingress_last_time_reg.write((bit<32>)hdr.myTunnel.flow_id, cur_time);
        }

        
        if (hdr.myTunnel.isValid()){
            myTunnel_operate.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    counter((MAX_TUNNEL_ID), CounterType.bytes) egress_byte_cnt;
    // remember the time of the last probe
    // register<time_t>(MAX_TUNNEL_ID) egress_last_time_reg;
    
    action strip_header(){
        hdr.myTunnel.setInvalid();
    }

    action count_packets(){
        egress_byte_cnt.count((bit<32>) hdr.myTunnel.flow_id);

        // bit<32> byte_cnt;
        // bit<32> new_byte_cnt;
        // time_t last_time;
        // time_t cur_time = standard_metadata.egress_global_timestamp;
        // // increment byte cnt for this packet's port
        // egress_byte_cnt_reg.read(byte_cnt, (bit<32>)hdr.myTunnel.flow_id);
        // new_byte_cnt = byte_cnt + standard_metadata.packet_length;
        // // reset the byte count when a probe packet passes through
        // egress_byte_cnt_reg.write((bit<32>)hdr.myTunnel.flow_id, new_byte_cnt);
        // egress_last_time_reg.write((bit<32>)hdr.myTunnel.flow_id, cur_time);

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
        count_packets();
        port_checker.apply();
        
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
	// update_checksum(
	//     hdr.ipv4.isValid(),
    //         { hdr.ipv4.version,
	//       hdr.ipv4.ihl,
    //           hdr.ipv4.diffserv,
    //           hdr.ipv4.totalLen,
    //           hdr.ipv4.identification,
    //           hdr.ipv4.flags,
    //           hdr.ipv4.fragOffset,
    //           hdr.ipv4.ttl,
    //           hdr.ipv4.protocol,
    //           hdr.ipv4.srcAddr,
    //           hdr.ipv4.dstAddr },
    //         hdr.ipv4.hdrChecksum,
    //         HashAlgorithm.csum16);
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
