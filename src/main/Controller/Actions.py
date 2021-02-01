#TODO: this may be overdone, fix this
class Action():
    def __init__(self):
        self.actions = {}

    def perform_action(self, action_name, **params):
        self.actions[action_name](**params)


class InsertTableEntry(Action):
    def __init__(self):
        super(self, Action).__init__()
        self.actions = {"insert_table_entry": self.insert_table_entry}

    def insert_table_entry(self, sw, table_entry):
        sw.WriteTableEntry(table_entry)

class InsertForwardingRule(Action):
    def __init__(self):
        super(self, Action).__init__()
        self.actions = {"insert_mutlicast_entry" : self.insert_mutlicast_entry}

    def insert_mutlicast_entry(self, sw, mcast_entry):
        sw.WritePREEntry(mcast_entry)



        

        
    