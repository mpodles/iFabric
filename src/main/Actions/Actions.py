#TODO: this may be overdone, fix this
class Action():
    def __init__(self):
        pass

    def perform_action(self, **params):
        pass


class InsertTableEntry(Action):
    def __init__(self):
        super(self, Action).__init__()     

    def perform_action(self, **params):
        sw = params["sw"]
        table_entry = params["table_entry"]
        sw.WriteTableEntry(table_entry)

class InsertForwardingRule(Action):
    def __init__(self):
        super(self, Action).__init__()

    def perform_action(self, **params):
        sw = params["sw"]
        mcast_entry = params["mcast_entry"]
        sw.WritePREEntry(mcast_entry)



        

        
    