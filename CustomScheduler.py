from mesa.time import RandomActivation
from Bee import Bee
from Resource import Resource
from BeeHive import BeeHive
from mesa import Agent
class CustomScheduler(RandomActivation):
    def __init__(self, model):
        super().__init__(model)
        self.all_agents = {
            BeeHive: {},
            Bee: {},
            Resource: {}
        }
        self.agent_order = [Resource, BeeHive, Bee]

    def add(self, agent: Agent) -> None:
        self._agents[agent.unique_id] = agent
        self.all_agents[type(agent)][agent.unique_id] = agent

    def remove(self, agent: Agent) -> None:
        del self._agents[agent.unique_id]
        del self.all_agents[type(agent)][agent.unique_id]

    def step(self) -> None:
        for agent_class in self.agent_order:
            self.step_for_each(agent_class)
        self.steps += 1

    def step_for_each(self, agent: Agent) -> None:
        for agent in self.all_agents[type(agent)].values():
            agent.step()

    def get_agent_count(self, agent_type) -> int:
        return len(self.all_agents[agent_type].values())



