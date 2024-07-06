from mesa import Agent, Model

from typing import Tuple
import numpy as np
from .BeeSwarm import BeeSwarm

from ..config.HiveConfig import HiveConfig
from ..config.BeeSwarmConfig import BeeSwarmConfig

class Hive(Agent):
    def __init__(
        self,
        model: Model,
        location: Tuple[int, int]
    ):
        super().__init__(model.next_id(), model)

        # Reference to the set of parameters governing Hive agent behaviour
        self.hive_config = model.hive_config

        # Reference to the set of parameters governing BeeSwarm agent behaviour
        self.beeswarm_config = model.beeswarm_config

        # TODO: Do we need Hive config if we unpack it anyway ?
        # TODO: Remove logic related to maturation and young bees.

        # Hive's position in space
        self.pos = location

        # Hive's effective radius ("close proximity") where bees can rest and communicate
        self.radius = self.hive_config.default_radius

        # Initial state of resources within the hive
        self.nectar = self.hive_config.default_nectar

        # Probability with which a young bee becomes a forager
        self.p_new_forager = self.hive_config.p_new_forager

    def feed_bees(self):
        """
        Feeds all bees within the hive.
        """
        # TODO: Implement

    def create_bee(self):
        """
        Creates a new adult bee agent.
        """
        self.young_bees -= 1
        self.nectar -= self.nectar_for_maturation
        self.model.create_agent(BeeSwarm, hive=self)
        self.young_bees += 1
        self.model.n_agents_existed += 1


    def step(self):
        """Agent's step function required by Mesa package."""
        self.feed_bees()
        self.mature_bees()
