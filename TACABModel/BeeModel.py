from __future__ import annotations
from mesa import Model
# from mesa.space import ContinuousSpace
# from mesa.datacollection import DataCollector
# from typing import List
from Bee import Bee
from Agent import Agent
from BeeHive import BeeHive


class BeeModel(Model):

    size: int
    n_agents_existed: int
    agents: List[Agent]

    day: int        # day of the year
    nsteps: int     # number of simulation steps

    def __init__(self: BeeModel, size: int, day:int=50):
        super().__init__()

        self.size = size
        self.space = ContinuousSpace(size, size, True)
        self.n_agents_existed = 0
        self.agents = []

        self.day = day
        self.nsteps = 0

        # TODO: Add foraging metrics from the literature, as defined in http://dx.doi.org/10.17221/7240-VETMED
        self.datacollector = DataCollector(
            model_reporters={
                "n_foragers": lambda x : len(list(filter(lambda bee : (bee.state == Bee.State.FORAGING), self.get_agents_of_type(Bee)))),
                "n_scouts": lambda x : len(list(filter(lambda bee : (bee.state == Bee.State.SCOUTING), self.get_agents_of_type(Bee)))),
                "n_resting": lambda x : len(list(filter(lambda bee : (bee.state == Bee.State.RESTING), self.get_agents_of_type(Bee)))) },
            agent_reporters={}              # As well as bee agent information
        )

    def create_agent(self, agent_type, **kwargs):
        agent = agent_type(self.n_agents_existed, self, **kwargs)
        self.agents.append(agent)
        self.space.place_agent(agent, agent.pos)
        self.n_agents_existed += 1
        return agent
    
    def create_agents(self, agent_type, n, **kwargs):
        agents = [self.create_agent(agent_type, **kwargs) for _ in range(n)]
        return agents

    def step(self):
        for agent in self.agents:
            # if isinstance(agent, Bee) and agent.is_foraging():
            #     self.space.move_agent(agent, agent.new_position())
            agent.step()
        
        self.nsteps += 1
        self.day = self.nsteps // (24 * 60 * 60)

        # TODO: Add interaction of agents (?)
        self.datacollector.collect(self)    # Record step variables in the DataCollector
        # TODO: self.schedule.step()