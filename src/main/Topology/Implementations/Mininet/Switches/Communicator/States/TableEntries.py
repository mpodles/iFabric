from p4.v1 import p4runtime_pb2

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

def get_state(action, communicator, **params):
    entries = ReadTableEntries(communicator)
    for response in entries:
        for entity in response.entities:
            entry = entity.table_entry
            table_name = communicator.device_data.p4info_helper.get_tables_name(entry.table_id)
            print '%s: ' % table_name,
            for m in entry.match:
                print communicator.device_data.p4info_helper.get_match_field_name(table_name, m.field_id),
                print '%r' % (communicator.device_data.p4info_helper.get_match_field_value(m),),
            action = entry.action.action
            action_name = communicator.device_data.p4info_helper.get_actions_name(action.action_id)
            print '->', action_name,
            for p in action.params:
                print communicator.device_data.p4info_helper.get_action_param_name(action_name, p.param_id),
                print '%r' % p.value,

def get_function():
    return get_state