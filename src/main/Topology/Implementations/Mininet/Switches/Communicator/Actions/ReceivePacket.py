from p4.v1 import p4runtime_pb2

def ReceivePacket(communicator, dry_run=False, **kwargs):
    request = p4runtime_pb2.StreamMessageRequest()
    if dry_run:
        print "P4 Runtime PacketIn: ", request 
    else:
        communicator.requests_stream.put(request)
        for item in communicator.stream_msg_resp:
            return item

def perform_action(action, communicator, **params):
    return ReceivePacket(communicator, **params)
def get_function():
    return perform_action