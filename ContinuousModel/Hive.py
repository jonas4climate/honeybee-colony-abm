from mesa import Agent, Model

from typing import Tuple

class Hive(Agent):
    
    # Class properties
    id: int                         # unique identifier, required in mesa package
    model: Model                    # model the agent belongs to

    location: Tuple[int, int]       # agent's current position, x and y coordinate
    radius: float                   # effective radius of the hive, within that radius bees are considered "inside the hive"
    
    nectar: float                   # Current amount of stored nectar
    water: float                    # Current amount of stored water
    pollen: float                   # Current amount of stored pollen
    
    young_bees: int                 # Number of non-forager bees (about to become foragers)

    # Class methods
    def __init__(self, id, model, location, radius=50.0, nectar=0.5, water=0.5, pollen=0.5, young_bees=0):
        super().__init__(id, model)

        self.location = location
        self.radius = radius
        
        self.nectar = nectar
        self.water = water
        self.pollen = pollen

        self.young_bees = young_bees
        self.p_new_forager = 0.0                    # TODO: If it's a function of reosurces, then this should be a class method

    def step(self):
        # 1. Feed bees
        # Get all young ones as well as foragers around beehive
        # Prioritize hunger ones! Turning water and pollen into bee health
        pass

        # 2. Mature bees
        # Use p_new_forager to instantiate bees
        pass
        # Then, update p_new_forager based on young, water, and pollen, and weather!!
        pass

        # 3. Create young bees
        # Based on resources and weather
        pass