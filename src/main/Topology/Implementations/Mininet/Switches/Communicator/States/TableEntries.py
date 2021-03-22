def get_function():
    return ReadTableEntries

def ReadTableEntries(communicator, table_id=None, dry_run=False):
    request = p4runtime_pb2.ReadRequest()
    request.device_id =  communicator.device.OSN_ID
    entity = request.entities.add()
    table_entry = entity.table_entry
    if table_id is not None:
        table_entry.table_id = table_id
    else:
        table_entry.table_id = 0
    if dry_run:
        print "P4Runtime Read:", request
    else:
        for response in communicator.client_stub.Read(request):
            yield response