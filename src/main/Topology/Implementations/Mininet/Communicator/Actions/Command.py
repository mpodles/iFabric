def get_function():
    return perform_action

def perform_action(action, communicator, **params):
    command(communicator, params**)
     
def command(communicator, command):
    communicator.device.cmd(command)
