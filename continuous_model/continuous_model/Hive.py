from mesa import Agent, Model

from typing import Tuple
import numpy as np
from mesa.datacollection import DataCollector
from .Bee import Bee
from .config import HiveConfig

class Hive(Agent):
    def __init__(
        self, 
        # id: int,  # unique identifier, required in mesa package
        model: Model,  # model the agent belongs to
        location: Tuple[int, int],  # agent's current position, x and y coordinate
        radius: float = HiveConfig.DEFAULT_RADIUS,  # effective radius of the hive, within that radius bees are considered "inside the hive"
        nectar: float = HiveConfig.DEFAULT_NECTAR,  # Current amount of stored nectar
        water: float = HiveConfig.DEFAULT_WATER,  # Current amount of stored water
        pollen: float = HiveConfig.DEFAULT_POLLEN,  # Current amount of stored pollen
        young_bees: int = HiveConfig.DEFAULT_YOUNG_BEES,  # Number of non-forager bees (about to become foragers
    ):
        super().__init__(model.next_id(), model)

        self.pos = location
        self.radius = radius

        self.nectar = nectar
        self.water = water
        self.pollen = pollen
        
        self.young_bees = young_bees
        self.p_new_forager = 0.0  # TODO: If it's a function of resources, then this should be a class method

        self.hive_health = 1
        self.feed_rate = HiveConfig.DEFAULT_FEED_RATE

    def feed_bees(self):
        # Get all young ones as well as foragers around beehive
        agents_in_hive = self.model.space.get_neighbors(self.pos, self.radius, include_center=True)
        bees_to_feed_in_hive = [agent for agent in agents_in_hive if type(agent) is Bee and agent.hive == self and agent.fed <= 1]
        # NOTE: skipped sorting, this is only relevant at a very short time point but requires lots of compute every iteration
        # sorted_bees = sorted([bee for bee in bees_to_feed_in_hive if bee.fed <= 1], key=lambda x: x.fed)
        feed_speed = self.feed_rate*self.model.dt
        for bee in bees_to_feed_in_hive:
            ## TODO: Prioritize hungery ones
            ## TODO: Use two resources
            if bee.fed <= 1 and self.nectar > feed_speed:
                bee.fed += feed_speed
                self.nectar -= feed_speed
        # healthy_bees = [bee for bee in bees_in_hive if bee.fed >= 0.5]

    def mature_bees(self):
        # This entails maturing young bees to foragers with some probability based on resources, weather etc...
        for _ in range(self.young_bees):
            if np.random.random() < self.p_new_forager:
                # self.model.create_agent(Bee, hive=self)
                self.young_bees -= 1

    def update_p_forager(self):
        ## TODO: Modify probability with resrouces
        self.p_new_forager = self.p_new_forager

    def create_bees(self):
        ## TODO: Update probability with resources, weather...
        p_new_young_bee = 0.1
        new_young = True if np.random.random() < p_new_young_bee else False
        if new_young:
            self.model.create_agent(Bee, hive=self)
            self.young_bees += 1
            self.model.n_agents_existed += 1

    # def kill_hive(self):
    #     bees_in_hive = [bee for bee in self.model.get_agents_of_type(Bee) if
    #                     bee.hive == self]
    #     # Kill the bees inside hive
    #     if self.nectar <= self.feed_rate:
    #         # Kill all bees since food ran out
    #         for bee in bees_in_hive:
    #             bee._remove_agent()
    #         print("Hive died due to lack of nectar")
    #         self.model.schedule.remove(self)
    #         self.model.space.remove_agent(self)
    #         self.model.n_agents_existed -= 1


    def step(self):
        # 1. Feed bees
        self.feed_bees()

        # 2. Mature bees
        # Use p_new_forager to instantiate bees
        self.mature_bees()


        # Then, update p_new_forager based on young, water, and pollen, and weather!!
        self.update_p_forager()

        # 3. Create young bees
        # Based on resources and weather
        self.create_bees()

        # 4. If nectar goes below 0, kill the hive
        # self.kill_hive()
