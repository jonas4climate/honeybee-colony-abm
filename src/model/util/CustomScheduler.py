from mesa.time import RandomActivation
from ..agents.BeeSwarm import BeeSwarm
from ..agents.Hive import Hive
from ..agents.Resource import Resource

import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

class CustomScheduler(RandomActivation):
    def __init__(self, model):
        super().__init__(model)
        self.all_agents = {
            BeeSwarm: {},
            Hive: {},
            Resource: {}
        }

        self.schedule_order = [Resource, Hive, BeeSwarm]
        self.bee_positions = []

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

    def step(self, locate_bees=None) -> None:
        for agent_class in self.schedule_order:
            self.step_for_each(agent_class)
            if agent_class == BeeSwarm:         # Uncomment for heatmap (slows down code otherwise)
                self.get_bee_positions()
        self.steps += 1

    def step_for_each(self, agent):
        agent_keys = list(self.all_agents[agent].keys())
        random.shuffle(agent_keys)
        # agent_type = type(agent)
        for agent_key in agent_keys:
            self.all_agents[agent][agent_key].step()

    def get_bee_count(self) -> int:
        """Get the number of bees in the model"""
        return len(self.all_agents[BeeSwarm].values())

    def get_bee_positions(self):
        for agent in self.all_agents[BeeSwarm].values():
            self.bee_positions.append(agent.pos)

    def make_heatmap(self, size, title="Heatmap of bee positions"):
        bee_positions = np.array(self.bee_positions)

        # noinspection PyTypeChecker
        heatmap, xedges, yedges = np.histogram2d(bee_positions[:, 0], bee_positions[:, 1], bins=20,
                                                 range=[[0, size], [0, size]])
        plt.figure(figsize=(10, 8))
        # noinspection PyTypeChecker
        plt.imshow(heatmap.T, norm=LogNorm(), origin='lower', cmap='hot', extent=[0, size, 0, size], alpha=1)
        plt.colorbar(label='Density')
        plt.title(title)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.show()