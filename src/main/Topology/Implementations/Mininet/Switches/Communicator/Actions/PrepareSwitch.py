from p4.tmp import p4config_pb2
from p4.v1 import p4runtime_pb2



def buildDeviceConfig(communicator):
    "Builds the device config for BMv2"
    device_config = p4config_pb2.P4DeviceConfig()
    device_config.reassign = True
    with open(communicator.device_data.p4_json_file_path) as f:
        device_config.device_data = f.read()
    return device_config

def MasterArbitrationUpdate(communicator, dry_run=False, **kwargs):
    print "MasterArbitrationUpdate"
    request = p4runtime_pb2.StreamMessageRequest()
    request.arbitration.device_id = communicator.device.OSN_ID
    request.arbitration.election_id.high = 0
    request.arbitration.election_id.low = 1
    if dry_run:
        print "P4Runtime MasterArbitrationUpdate: ", request
    else:
        communicator.requests_stream.put(request)
        for item in communicator.stream_msg_resp:
            return item # just one
def SetForwardingPipelineConfig(communicator, dry_run=False):
    print "SetForwardingPipelineConfig"
    device_config = buildDeviceConfig(communicator)
    request = p4runtime_pb2.SetForwardingPipelineConfigRequest()
    request.election_id.low = 1
    request.device_id = communicator.device.OSN_ID
    config = request.config
    config.p4info.CopyFrom(communicator.device_data.p4info_helper.p4info)
    config.p4_device_config = device_config.SerializeToString()
    request.action = p4runtime_pb2.SetForwardingPipelineConfigRequest.VERIFY_AND_COMMIT
    if dry_run:
        print "P4Runtime SetForwardingPipelineConfig:", request
    else:
        communicator.client_stub.SetForwardingPipelineConfig(request)
def get_switch_ready(communicator):
    MasterArbitrationUpdate(communicator)
    SetForwardingPipelineConfig(communicator)
def perform_action(action, communicator, **params):
    get_switch_ready(communicator)
def get_function():
    return perform_action

