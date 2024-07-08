from mesa import Agent, Model

from typing import Tuple
from numpy.random import random
from .BeeSwarm import BeeSwarm

from ..config.BeeSwarmConfig import BeeSwarmConfig as BSC
from ..config.HiveConfig import HiveConfig as HC

class Hive(Agent):

    def __init__(
        self,
        model: Model
    ):
        super().__init__(model.next_id(), model)

        # Hive's position in space, initialization done through ContinousSpace.place_agent()
        self.pos = None

        # Initial state of resources within the hive
        self.nectar = HC.DEFAULT_INIT_NECTAR

    def feed_bees(self):
        """
        Feeds all bees within the hive.
        """
        bees_in_hive = self.model.get_agents_of_type(BeeSwarm)
        bees_in_hive = list(filter(lambda bee : isinstance(bee, BeeSwarm) and bee.is_in_hive, bees_in_hive))

        self.nectar = max(0, self.nectar - len(bees_in_hive) * self.model.bee_config.FOOD_CONSUMPTION)

    def create_bee(self):
        """
        Creates a new adult bee agent.
        """
        self.model.create_agent(BeeSwarm, self.pos, hive=self)
            
    def step(self):
        """Agent's step function required by Mesa package."""
        self.feed_bees()
        
        if random() < HC.P_BIRTH:
            self.create_bee()
        
