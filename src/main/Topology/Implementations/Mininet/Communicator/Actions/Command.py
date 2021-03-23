def get_function():
    return perform_action

def perform_action(action, communicator, **params):
    return command(communicator, **params)
     
def command(communicator, command):
    return communicator.device.cmd(command)
