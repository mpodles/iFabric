class OSNetAction(object):
    def __init__(self, name, action_function):
        self.name = name
        self.action_function = action_function
        self.action_log = {}

    def __call__(self, **params):
        self.action_function(**params)

    def log_message(self):
        pass #TODO: think of good loging system maybe with decorators





        

        
    