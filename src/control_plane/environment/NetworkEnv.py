import gym
from gym import spaces


NUMBER_OF_SWITCHES = 6
NUMBER_OF_PORTS_PER_SWITCH = 48
NUMBER_OF_FLOWS=20

class NetworkEnv(gym.Env):

    def __init__(self):
        super(NetworkEnv,self).__init__()
        self.action_space = spaces.Box(low=0, high=20, shape=(NUMBER_OF_SWITCHES, NUMBER_OF_PORTS_PER_SWITCH, NUMBER_OF_FLOWS, 2))
        self.observation_space = spaces.Box(low=0, high=NUMBER_OF_PORTS_PER_SWITCH, shape=(NUMBER_OF_SWITCHES, NUMBER_OF_FLOWS) )
        print(self.action_space)

if __name__ == "__main__":
    env = NetworkEnv()
    print(env.action_space.sample())