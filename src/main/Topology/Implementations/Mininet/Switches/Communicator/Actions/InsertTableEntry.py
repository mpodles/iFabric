def get_function():
    return perform_action
def perform_action(action, communicator, **params):
    table_entry = communicator.p4info_helper.buildTableEntry(
        **params)
        # table_name=table_name,
        # match_fields=match_fields,
        # default_action=default_action,
        # action_name=action_name,
        # action_params=action_params,
        # priority=priority)
    WriteTableEntry(communicator, table_entry)
        
def WriteTableEntry(communicator, table_entry, dry_run=False):
    request = p4runtime_pb2.WriteRequest()
    request.device_id = communicator.device.OSN_ID 
    request.election_id.low = 1
    update = request.updates.add()
    if table_entry.is_default_action:
        update.type = p4runtime_pb2.Update.MODIFY
    else:
        update.type = p4runtime_pb2.Update.INSERT
    update.entity.table_entry.CopyFrom(table_entry)
    if dry_run:
        print "P4Runtime Write:", request
    else:
        communicator.client_stub.Write(request)