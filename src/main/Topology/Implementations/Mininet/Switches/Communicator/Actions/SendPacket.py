from p4.v1 import p4runtime_pb2
def PacketOut(communicator, packet, dry_run=False, **kwargs):
        request = p4runtime_pb2.StreamMessageRequest()
        request.packet.CopyFrom(packet)
        if dry_run:
            print "P4 Runtime WritePacketOut: ", request 
        else:
            communicator.requests_stream.put(request)
            for item in communicator.stream_msg_resp:
                return item

def perform_action(action, communicator, **params):
     return PacketOut(communicator, **params)
def get_function():
    return perform_action