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

        # Number of young bees which can mature to foragers
        self.young_bees = self.hive_config.init_young_bees

        # Probability with which a young bee becomes a forager
        self.p_new_forager = self.hive_config.p_new_forager

        # Maximal nectar capacity within the hive
        self.max_nectar_capacity = self.hive_config.max_nectar_capacity

        # Nectar required for maturation of a young bee
        self.nectar_for_maturation = 0

    def feed_bees(self):
        """
        Feeds all bees within the hive.
        """
        # Get all the bee agents within the hive
        agents_in_hive = self.model.space.get_neighbors(self.pos, self.radius, include_center=True)
        bees_to_feed_in_hive = [agent for agent in agents_in_hive if type(agent) is BeeSwarm and agent.hive == self and agent.fed <= self.beeswarm_config.feed_storage]

        # Feeds all the bees taking care of the available resources
        # TODO: If we get rid of hunger logic, we can "parallelize" it by multiplying number of bees in hive by a constant
        for bee in bees_to_feed_in_hive:
            if self.nectar == 0:
                break
            feed_amount = min(self.beeswarm_config.feed_storage - bee.fed, self.nectar)
            bee.fed += feed_amount
            self.nectar -= feed_amount

    def mature_bees(self):
        """
        Matures the young population into adult bees.
        """
        # TODO: Remove (?) We don't use it.

        # Probability of young bee maturing
        p_new_bee = self.p_new_forager*self.model.dt

        # Matures all bees using available resources
        for _ in range(self.young_bees):
            if self.nectar < self.nectar_for_maturation:
                break
            if np.random.random() < p_new_bee:
                self.create_bee()

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
