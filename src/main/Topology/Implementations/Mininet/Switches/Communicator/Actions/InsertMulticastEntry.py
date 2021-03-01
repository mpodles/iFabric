def perform_action(self, **params):
    mc_entry = self.p4info_helper.buildMulticastGroupEntry(params["multicast_group_id"], params['replicas'])
    self.WritePREEntry(mc_entry)
def WritePREEntry(self, pre_entry, dry_run=False, modify=False):
    request = p4runtime_pb2.WriteRequest()
    request.device_id = self.ID
    request.election_id.low = 1
    update = request.updates.add()
    if modify:
        update.type = p4runtime_pb2.Update.MODIFY
    else:
        update.type = p4runtime_pb2.Update.INSERT
    update.entity.packet_replication_engine_entry.CopyFrom(pre_entry)
    if dry_run:
        print "P4Runtime Write Multicast:", request
    else:
        # print "Writing entry", request
        self.client_stub.Write(request)
