"""
Model 1
Jonas, Bartek and Pablo
Based on the PDF Pablo sent on Saturday.
"""

from mesa import  Agent, Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation

from typing import List

from .Bee import Bee
from .Hive import Hive
from .Resource import Resource

class ForagerModel(Model):

    # Class properties
    size: int                   # side length of the square-shaped continuous space
    n_agents_existed: int       # counter for all the agents that were added to the model
    
    space: ContinuousSpace      # continous space container from mesa package
    agents: List[Agent]         # current list of agents

    # Class methods
    def __init__(self, SIZE, n_hives, hive_locations, n_bees_per_hive, n_resources, resource_locations):
        super().__init__()

        self.size = SIZE
        self.n_agents_existed = 0

        self.space = ContinuousSpace(SIZE, SIZE, True)
        self.schedule = RandomActivation(self)
        self.agents = []

        # TODO: Add foraging metrics from the literature, as defined in http://dx.doi.org/10.17221/7240-VETMED
        self.datacollector = DataCollector(
            model_reporters={},             # Collect metrics from literature at every step
            agent_reporters={}              # As well as bee agent information
        )

        self.make_agents(n_hives, hive_locations, n_bees_per_hive, n_resources, resource_locations)

    def create_agent(self, agent_type, **kwargs):
        agent = agent_type(self.n_agents_existed, self, **kwargs)
        self.agents.append(agent)
        self.space.place_agent(agent, agent.pos)
        self.schedule.add(agent)
        self.n_agents_existed += 1
        return agent
    
    def create_agents(self, agent_type, n, **kwargs):
        agents = [self.create_agent(agent_type, **kwargs) for _ in range(n)]
        return agents
    
    def make_agents(self, n_hives, hive_locations, n_bees_per_hive, n_resources, resource_locations):
        assert len(hive_locations) == n_hives
        assert len(n_bees_per_hive) == n_hives
        assert len(resource_locations) == n_resources
        
        # Create Hives with their corresponding Bee agents
        for i in range(n_hives):
            current_hive = self.create_agent(Hive, location=hive_locations[i])
            for _ in range(n_bees_per_hive[i]):
                self.create_agent(Bee, hive=current_hive)
        
        # Create Resources
        for i in range(n_resources):
            self.create_agent(Resource, location=resource_locations[i])

    def step(self):
        for agent in self.agents:
            agent.step()
        # TODO: Add interaction of agents (?)
        self.datacollector.collect(self)    # Record step variables in the DataCollector
        # TODO: self.schedule.step()