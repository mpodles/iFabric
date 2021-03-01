def get_state_data(self):
    self.latest_state_data = self.ReadCounters()
    return self.latest_state_data
def ReadCounters(self, counter_id=None, index=None, dry_run=False):
    request = p4runtime_pb2.ReadRequest()
    request.device_id = self.ID
    entity = request.entities.add()
    counter_entry = entity.counter_entry
    if counter_id is not None:
        counter_entry.counter_id = counter_id
    else:
        counter_entry.counter_id = 0
    if index is not None:
        counter_entry.index.index = index
    if dry_run:
        print "P4Runtime Read:", request
    else:
        for response in self.client_stub.Read(request):
            yield response
