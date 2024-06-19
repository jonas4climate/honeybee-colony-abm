from mesa.time import RandomActivation
from Bee import Bee; from Resource import Resource; from BeeHive import BeeHive
import random
# from model import BeeModel

# model = BeeModel()
# hive = BeeHive(model, (50,50))
# bee = Bee(model, (50,50), hive)
#
# agent_type = type(bee)
# all_agents[agent_type][bee.unique_id] = bee
#
# type(hive)


class CustomScheduler(RandomActivation):
    def __init__(self, model):
        super().__init__(model)
        self.all_agents = {
            BeeHive: {},
            Bee: {},
            Resource: {}
        }

        self.schedule_order = [Resource, BeeHive, Bee]

    def add(self, agent):
        self._agents[agent.unique_id] = agent
        agent_type = type(agent)
        self.all_agents[agent_type][agent.unique_id] = agent

    def remove(self, agent):
        del self._agents[agent.unique_id]
        agent_type = type(agent)
        del self.all_agents[agent_type][agent.unique_id]

    def step(self) -> None:
        for agent_class in self.schedule_order:
            self.step_for_each(agent_class)
        self.steps += 1

    def step_for_each(self, agent):
        agent_keys = list(self.all_agents[agent].keys())
        random.shuffle(agent_keys)
        for agent_key in agent_keys:
            self.all_agents[agent][agent_key].step()

    def get_agent_count(self, agent) -> int:
        agent_type = type(agent)
        return len(self.all_agents[agent].values())



