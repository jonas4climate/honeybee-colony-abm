from mesa import Agent, Model

from typing import Tuple
import numpy as np
from mesa.datacollection import DataCollector
from .Bee import Bee

class Hive(Agent):
    
    # Class properties
    id: int                         # unique identifier, required in mesa package
    model: Model                    # model the agent belongs to

    pos: Tuple[int, int]            # agent's current position, x and y coordinate
    radius: float                   # effective radius of the hive, within that radius bees are considered "inside the hive"
    
    nectar: float                   # Current amount of stored nectar
    # water: float                    # Current amount of stored water
    # pollen: float                   # Current amount of stored pollen
    
    young_bees: int                 # Number of non-forager bees (about to become foragers)

    # Class constants
    RADIUS = 20                     # for drawing in Javascript server visualization

    # Class methods
    def __init__(self, id, model, location, radius=10.0, nectar=0.5, water=0.5, pollen=0.5, young_bees=0):
        super().__init__(id, model)
        self.id = id
        self.pos = location
        self.radius = radius
        
        self.nectar = nectar
        self.water = water
        self.pollen = pollen

        self.young_bees = young_bees
        self.p_new_forager = 0.0                    # TODO: If it's a function of reosurces, then this should be a class method

    def feed_bees(self):
        # Get all young ones as well as foragers around beehive
        bees_in_hive = [bee for bee in self.model.get_agents_of_type(Bee) if bee.hive == self and bee.distance_to_agent(self) <= self.radius]
        # Sort them by hunger
        sorted_bees = sorted([bee for bee in bees_in_hive if bee.fed < 1], key=lambda x: x.fed)
        for bee in sorted_bees:
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
            self.model.n_agents_existed += 1

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
