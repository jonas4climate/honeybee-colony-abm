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
        radius: float = HiveConfig.DEFAULT_RADIUS,  # effective radius of the hive, within that radius bees are considered "inside the hive"
        nectar: float = HiveConfig.DEFAULT_NECTAR,  # Current amount of stored nectar
        young_bees: int = HiveConfig.INIT_YOUNG_BEES,  # Number of non-forager bees (about to become foragers
        p_new_forager: float = HiveConfig.P_NEW_FORAGER
    ):
        super().__init__(model.next_id(), model)

        self.pos = location
        self.radius = radius

        assert 0.0 <= nectar and nectar <= 1.0, "Nectar quantity should be normalized."
        self.nectar = nectar
        
        self.young_bees = young_bees
        self.p_new_forager = p_new_forager
        # NOTE: Simplification - at the moment bees grow up, they use up nectar equivalent to the average growth time * starvation speed
        self.nectar_for_maturation = BeeSwarmConfig.STARVATION_SPEED/p_new_forager

        self.hive_health = 1
        self.feed_rate = HiveConfig.FEED_RATE

    def feed_bees(self):
        # Get all young ones as well as foragers around beehive
        agents_in_hive = self.model.space.get_neighbors(self.pos, self.radius, include_center=True)
        bees_to_feed_in_hive = [agent for agent in agents_in_hive if type(agent) is BeeSwarm and agent.hive == self and agent.fed <= BeeSwarmConfig.FEED_STORAGE]
        # NOTE: skipped sorting, this is only relevant at a very short time point but requires lots of compute every iteration
        # sorted_bees = sorted([bee for bee in bees_to_feed_in_hive if bee.fed <= 1], key=lambda x: x.fed)
        for bee in bees_to_feed_in_hive:
            if self.nectar == 0:
                break
            feed_amount = min(BeeSwarmConfig.FEED_STORAGE - bee.fed, self.nectar)
            bee.fed += feed_amount
            self.nectar -= feed_amount

    def mature_bees(self):
        p_new_bee = self.p_new_forager*self.model.dt
        for _ in range(self.young_bees):
            if self.nectar < self.nectar_for_maturation:
                return
            if np.random.random() < p_new_bee:
                self.create_bee()

    def update_p_forager(self):
        ## TODO: Modify probability with resrouces
        self.p_new_forager = self.p_new_forager

    def create_bee(self):
        print('A bee grew up to become a forager')
        self.young_bees -= 1
        self.nectar -= self.nectar_for_maturation
        assert self.nectar < 0, "Used up more nectar than possible during maturation of young bee"
        self.model.create_agent(BeeSwarm, hive=self)
        self.young_bees += 1
        self.model.n_agents_existed += 1


    def step(self):
        self.feed_bees()
        self.mature_bees()
        # self.kill_hive()
