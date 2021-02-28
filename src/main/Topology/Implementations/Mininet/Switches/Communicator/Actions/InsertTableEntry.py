class InsertTableEntry(Action):
    def __init__(self):
        super(self, Action).__init__()     

    def perform_action(self, **params):
        sw = params["sw"]
        table_entry = params["table_entry"]
        sw.WriteTableEntry(table_entry)