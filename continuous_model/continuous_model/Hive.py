from mesa import Agent, Model

from typing import Tuple
from continuous_model.Bee import Bee
from random import random


def feed_bees(self):
    # Get all young ones as well as foragers around beehive
    ## Right now this entails bees around beehive up to 1.5*radius
    bees_in_hive = [other_agent for other_agent in self.model.agents if other_agent != self and ((other_agent.pos[0] - self.pos[0])**2 + (other_agent.pos[1] - self.pos[1])**2)**0.5 <= (self.radius*1.5) and isinstance(other_agent, Bee)]

    for bee in bees_in_hive:
        # Feed it, recall maximum health and that there should be resources
        ## TODO: Prioritize hunger ones! Turning water and pollen into bee health
        ## TODO: Use two resources
        if bee.fed <= 1 and self.nectar > 0.01:
            bee.fed += 0.01
            self.nectar -= 0.01

def mature_bees(self):
    # This entails maturing young bees to foragers with some probability based on resources, weather etc...
    for young_bee in range(self.young_bees):
        mature = True if random() < self.p_new_forager else False
        if mature:
            new_forager = Bee(self,fov=0.5, age=4, health=1, state="resting", wiggle=False)
            self.grid.place_agent(new_forager, (0, 0))
            self.young_bees -= 1
    

def update_p_forager(self):
    ## TODO: Modify probability with resrouces
    self.p_new_forager = self.p_new_forager
    

def create_bees(self):
    ## TODO: Update probability with resources, weather...
    p_new_young_bee = 0.1
    new_young = True if random() < p_new_young_bee else False
    if new_young:
        self.young_bees += 1


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

        self.pos = location
        self.radius = radius
        
        self.nectar = nectar
        self.water = water
        self.pollen = pollen

        self.young_bees = young_bees
        self.p_new_forager = 0.0                    # TODO: If it's a function of reosurces, then this should be a class method


    def step(self):
        # 1. Feed bees
        feed_bees(self)

        # 2. Mature bees
        # Use p_new_forager to instantiate bees
        mature_bees(self)


        # Then, update p_new_forager based on young, water, and pollen, and weather!!
        update_p_forager(self)

        # 3. Create young bees
        # Based on resources and weather
        create_bees(self)
