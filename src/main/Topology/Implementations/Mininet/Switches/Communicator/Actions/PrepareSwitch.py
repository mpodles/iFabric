def get_function():
    return perform_action
def perform_action(self, **params):
    self.get_switch_ready()
def get_switch_ready(self):
    self.MasterArbitrationUpdate()
    self.SetForwardingPipelineConfig()
def MasterArbitrationUpdate(self, dry_run=False, **kwargs):
    request = p4runtime_pb2.StreamMessageRequest()
    request.arbitration.device_id = self.OSN_ID
    request.arbitration.election_id.high = 0
    request.arbitration.election_id.low = 1
    if dry_run:
        print "P4Runtime MasterArbitrationUpdate: ", request
    else:
        self.requests_stream.put(request)
        for item in self.stream_msg_resp:
            return item # just one
def SetForwardingPipelineConfig(self, dry_run=False):
    device_config = self.buildDeviceConfig()
    request = p4runtime_pb2.SetForwardingPipelineConfigRequest()
    request.election_id.low = 1
    request.device_id = self.OSN_ID
    config = request.config
    config.p4info.CopyFrom(self.p4info_helper)
    config.p4_device_config = device_config.SerializeToString()
    request.action = p4runtime_pb2.SetForwardingPipelineConfigRequest.VERIFY_AND_COMMIT
    if dry_run:
        print "P4Runtime SetForwardingPipelineConfig:", request
    else:
        self.client_stub.SetForwardingPipelineConfig(request)
def buildDeviceConfig(self):
    "Builds the device config for BMv2"
    device_config = p4config_pb2.P4DeviceConfig()
    device_config.reassign = True
    device_config.device_data = self.p4_json_file_path
    return device_config