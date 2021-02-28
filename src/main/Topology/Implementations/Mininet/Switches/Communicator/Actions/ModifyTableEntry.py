import sys
sys.path.append('/home/mpodles/iFabric/src/main/Topology/Skeleton/Communicator')
from OSNetAction import OSNetAction
class InsertTableEntry(OSNetAction):
    def __init__(self):
        OSNetAction.__init__(self)    


    def perform_action(self, **params):
        flow = params["flow"]
        table_entry = self.build_table_entry(flow)
        self.WriteTableEntry(table_entry)

    def build_table_entry(self, flow):
        table_name = flow['table']
        match_fields = flow.get('match') # None if not found
        action_name = flow['action_name']
        default_action = flow.get('default_action') # None if not found
        action_params = flow['action_params']
        priority = flow.get('priority')  # None if not found

        table_entry = self.p4info_helper.buildTableEntry(
            table_name=table_name,
            match_fields=match_fields,
            default_action=default_action,
            action_name=action_name,
            action_params=action_params,
            priority=priority)
        
        return table_entry
            
    def WriteTableEntry(self, table_entry, dry_run=False):
        request = p4runtime_pb2.WriteRequest()
        request.device_id = self.ID
        request.election_id.low = 1
        update = request.updates.add()
        update.type = p4runtime_pb2.Update.MODIFY
        update.entity.table_entry.CopyFrom(table_entry)
        if dry_run:
            print "P4Runtime Write:", request
        else:
            self.client_stub.Write(request)
