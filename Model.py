from BeeModelGrid import BeeModelGrid
from mesa import Model
from set_parameters import WIDTH, HEIGHT
from mesa.datacollection import DataCollector

class BeeModel(Model):
    def __init__(self, width=WIDTH, height=HEIGHT):
        super().__init__()
        # self.size = SIZE                                        # Int: Size of the square space considered for the simulation
        self.space = BeeModelGrid(width, height, True)
        self.n_agents_existed = 0                               # Counter for all agents to have created, used as unique id
        self.agents = []                                        # List of all agents in the model

        # TODO: Add foraging metrics from the literature, as defined in http://dx.doi.org/10.17221/7240-VETMED
        self.datacollector = DataCollector(
            model_reporters={},             # Collect metrics from literature at every step
            agent_reporters={}              # As well as bee agent information
        )

    def create_agent(self, agent_type, **kwargs):
        agent = agent_type(self.n_agents_existed, self, **kwargs)
        self.agents.append(agent)
        self.space.place_agent(agent, agent.location)
        self.n_agents_existed += 1
        return agent
    
    def create_agents(self, agent_type, n, **kwargs):
        agents = [self.create_agent(agent_type, **kwargs) for _ in range(n)]
        return agents

    def step(self):
        for agent in self.agents:
            agent.step()
        # TODO: Add interaction of agents (?)
        self.datacollector.collect(self)    # Record step variables in the DataCollector
        # TODO: self.schedule.step()
