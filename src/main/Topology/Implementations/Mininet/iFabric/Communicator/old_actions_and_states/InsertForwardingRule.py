class InsertForwardingRule(Action):
    def __init__(self):
        super(self, Action).__init__()

    def perform_action(self, **params):
        sw = params["sw"]
        mcast_entry = params["mcast_entry"]
        sw.WritePREEntry(mcast_entry)
