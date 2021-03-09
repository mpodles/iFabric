def ReadCounters(communicator, port=None, flow_id = None, dry_run=False):
    index = port + (flow_id-1)*48
    counter_id = communicator.device.p4info_helper.get_counters_id("MyIngress.ingress_byte_cnt")
    request = p4runtime_pb2.ReadRequest()
    request.device_id = self.OSN_ID
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
        for response in communicator.client_stub.Read(request):
            yield response

def get_state(action, communicator, **params):
    state = ReadCounters(communicator, **params)
    for response in state:
        for entity in state.entities:
            counter = entity.counter_entry
            return counter.data.byte_count


def get_function():
    return get_state


