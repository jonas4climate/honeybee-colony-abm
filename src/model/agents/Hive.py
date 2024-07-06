from mesa import Agent, Model

from typing import Tuple
import numpy as np
from numpy.random import random
from .BeeSwarm import BeeSwarm

class Hive(Agent):

    RADIUS = 10
    P_NEW_FORAGER = 0.05

    def __init__(
        self,
        model: Model,
        location: Tuple[int, int]
    ):
        super().__init__(model.next_id(), model)

        # Hive's position in space
        self.pos = location

        # Initial state of resources within the hive
        self.nectar = self.model.hive_config.default_nectar

    def feed_bees(self):
        """
        Feeds all bees within the hive.
        """
        bees_in_hive = self.model.get_agents_of_type(BeeSwarm)
        bees_in_hive = list(filter(lambda bee : isinstance(bee, BeeSwarm) and bee.is_exploring, bees_in_hive))

        self.nectar = max(0, len(bees_in_hive) * BeeSwarm.FOOD_CONSUMPTION)

    def create_bee(self):
        """
        Creates a new adult bee agent.
        """
        self.model.create_agent(BeeSwarm, hive=self)
            
    def step(self):
        """Agent's step function required by Mesa package."""
        self.feed_bees()
        if random() < Hive.P_NEW_FORAGER:
            self.create_bee()
        
