from mesa import Agent, Model

from typing import Tuple
import numpy as np
from mesa.datacollection import DataCollector
from .Bee import BeeSwarm
from .config import HiveConfig, BeeSwarmConfig

class Hive(Agent):
    def __init__(
        self, 
        # id: int,  # unique identifier, required in mesa package
        model: Model,  # model the agent belongs to
        location: Tuple[int, int],  # agent's current position, x and y coordinate
        nectar: float = HiveConfig.DEFAULT_NECTAR,  # Current amount of stored nectar
    ):
        super().__init__(model.next_id(), model)

        self.pos = location

        assert 0.0 <= nectar and nectar <= 1.0, "Nectar quantity should be normalized."
        self.nectar = nectar

    def step(self):
        # TODO: Readd resource depletion
        pass