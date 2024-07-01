from mesa.time import RandomActivation
from .Bee import BeeSwarm
from .Hive import Hive
from .Resource import Resource
import random
class CustomScheduler(RandomActivation):
    def __init__(self, model):
        super().__init__(model)
        self.all_agents = {
            BeeSwarm: {},
            Hive: {},
            Resource: {}
        }

        self.schedule_order = [Resource, Hive, BeeSwarm]
        # self.agents = {}
    def add(self, agent):
        if agent not in self._agents:
            self._agents.add(agent)
        else:
            raise ValueError("agent already added to scheduler")
        agent_type = type(agent)
        self.all_agents[agent_type][agent.unique_id] = agent

    def remove(self, agent):
        self._agents.remove(agent)
        agent_type = type(agent)
        del self.all_agents[agent_type][agent.unique_id]

    def step(self) -> None:
        for agent_class in self.schedule_order:
            self.step_for_each(agent_class)
        self.steps += 1

    def step_for_each(self, agent):
        agent_keys = list(self.all_agents[agent].keys())
        random.shuffle(agent_keys)
        # agent_type = type(agent)
        for agent_key in agent_keys:
            self.all_agents[agent][agent_key].step()

    def get_bee_count(self) -> int:
        return len(self.all_agents[BeeSwarm].values())



