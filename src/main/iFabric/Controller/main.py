from Agent import Agent


def main():
    topology = read_topology()
    agent = Agent(topology=topology, other_agents= None)
    agent.operate()

def read_topology():
    return {}

if __name__ == "__main__":
    main()