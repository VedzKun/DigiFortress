from src.agent.agent import Agent
from src.redteam.minja_runner import MINJARunner

if __name__ == "__main__":
    agent = Agent()
    minja = MINJARunner(agent)
    minja.run()
