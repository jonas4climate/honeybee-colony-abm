from mesa import Agent, Model

from typing import Tuple
import numpy as np
from .Bee import BeeSwarm
from ..config.config import HiveConfig, BeeSwarmConfig

class Hive(Agent):
    def __init__(
        self, 
        # id: int,  # unique identifier, required in mesa package
        model: Model,  # model the agent belongs to
        location: Tuple[int, int]
    ):
        super().__init__(model.next_id(), model)
        hive_config = model.hive_config
        beeswarm_config = model.beeswarm_config

        self.pos = location
        self.radius = hive_config.default_radius
        self.nectar = hive_config.default_nectar
        self.young_bees = hive_config.init_young_bees
        self.p_new_forager = hive_config.p_new_forager
        self.max_nectar_capacity = hive_config.max_nectar_capacity
        self.nectar_for_maturation = 0 # NOTE: Assumption that bees need no resources to mature
        self.beeswarm_feed_storage = beeswarm_config.feed_storage # just here for reference, belongs to BeeSwarm

        self.hive_health = 1

    def feed_bees(self):
        # Get all young ones as well as foragers around beehive
        agents_in_hive = self.model.space.get_neighbors(self.pos, self.radius, include_center=True)
        bees_to_feed_in_hive = [agent for agent in agents_in_hive if type(agent) is BeeSwarm and agent.hive == self and agent.fed <= self.beeswarm_feed_storage]
        # NOTE: skipped sorting, this is only relevant at a very short time point but requires lots of compute every iteration
        # sorted_bees = sorted([bee for bee in bees_to_feed_in_hive if bee.fed <= 1], key=lambda x: x.fed)
        for bee in bees_to_feed_in_hive:
            if self.nectar == 0:
                break
            feed_amount = min(self.beeswarm_feed_storage - bee.fed, self.nectar)
            bee.fed += feed_amount
            self.nectar -= feed_amount

    def mature_bees(self):
        p_new_bee = self.p_new_forager*self.model.dt
        for _ in range(self.young_bees):
            if self.nectar < self.nectar_for_maturation:
                break
            if np.random.random() < p_new_bee:
                self.create_bee()

    def update_p_forager(self):
        ## TODO: Modify probability with resrouces
        self.p_new_forager = self.p_new_forager

    def create_bee(self):
        print('A bee grew up to become a forager')
        self.young_bees -= 1
        self.nectar -= self.nectar_for_maturation
        self.model.create_agent(BeeSwarm, hive=self)
        self.young_bees += 1
        self.model.n_agents_existed += 1


    def step(self):
        self.feed_bees()
        self.mature_bees()
        # self.kill_hive()
