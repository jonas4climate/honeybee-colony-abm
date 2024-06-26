from mesa import Agent, Model

from typing import Tuple
import numpy as np

from .Bee import Bee
from .config import HiveConfig

class Hive(Agent):
    def __init__(
        self, 
        id: int,  # unique identifier, required in mesa package
        model: 'Model',  # model the agent belongs to
        location: Tuple[int, int],  # agent's current position, x and y coordinate
        radius: float = HiveConfig.DEFAULT_RADIUS,  # effective radius of the hive, within that radius bees are considered "inside the hive"
        nectar: float = HiveConfig.DEFAULT_NECTAR,  # Current amount of stored nectar
        water: float = HiveConfig.DEFAULT_WATER,  # Current amount of stored water
        pollen: float = HiveConfig.DEFAULT_POLLEN,  # Current amount of stored pollen
        young_bees: int = HiveConfig.DEFAULT_YOUNG_BEES  # Number of non-forager bees (about to become foragers
    ):
        super().__init__(id, model)
        
        self.pos = location
        self.radius = radius

        self.nectar = nectar
        self.water = water
        self.pollen = pollen
        
        self.young_bees = young_bees
        self.p_new_forager = 0.0  # TODO: If it's a function of resources, then this should be a class method

    def feed_bees(self):
        # Get all young ones as well as foragers around beehive
        bees_in_hive = [bee for bee in self.model.get_agents_of_type(Bee) if bee.hive == self and bee.distance_to_agent(self) <= self.radius]

        for bee in bees_in_hive:
            # Feed it, recall maximum health and that there should be resources
            ## TODO: Prioritize hunger ones! Turning water and pollen into bee health
            ## TODO: Use two resources
            if bee.fed <= 1 and self.nectar > 0.01:
                bee.fed += 0.01
                self.nectar -= 0.01

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
            self.young_bees += 1

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
