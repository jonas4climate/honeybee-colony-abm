"""
Model 1
Jonas, Bartek and Pablo
Based on the PDF Pablo sent on Saturday.
"""

from mesa import  Agent, Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector

from typing import List

class Model(Model):

    # Class properties
    size: int                   # side length of the square-shaped continuous space
    n_agents_existed: int       # counter for all the agents that were added to the model
    
    space: ContinuousSpace      # continous space container from mesa package
    agents: List[Agent]         # current list of agents

    # Class methods
    def __init__(self, SIZE):
        super().__init__()

        self.size = SIZE
        self.n_agents_existed = 0

        self.space = ContinuousSpace(SIZE, SIZE, True)
        self.agents = []

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