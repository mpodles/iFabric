def get_function():
    return ReadTableEntries

def ReadTableEntries(self, table_id=None, dry_run=False):
    request = p4runtime_pb2.ReadRequest()
    request.device_id =  self.OSN_ID
    entity = request.entities.add()
    table_entry = entity.table_entry
    if table_id is not None:
        table_entry.table_id = table_id
    else:
        table_entry.table_id = 0
    if dry_run:
        print "P4Runtime Read:", request
    else:
        for response in self.client_stub.Read(request):
            yield response