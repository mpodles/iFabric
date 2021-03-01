def get_function(self):
    return ReadTableEntries

def ReadTableEntries(self, id, client_stub, table_id=None, dry_run=False):
    request = p4runtime_pb2.ReadRequest()
    request.device_id =  id
    entity = request.entities.add()
    table_entry = entity.table_entry
    if table_id is not None:
        table_entry.table_id = table_id
    else:
        table_entry.table_id = 0
    if dry_run:
        print "P4Runtime Read:", request
    else:
        for response in client_stub.Read(request):
            yield response