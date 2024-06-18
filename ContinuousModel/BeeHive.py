# import mesa
from mesa import Agent
# from mesa.space import ContinuousSpace
# from mesa.datacollection import DataCollector

class BeeHive(Agent):
    def __init__(self, id, model, location, radius, water, pollen, young_bees, p_new_forager):
        super().__init__(id, model)
        self.location = location
        self.radius = radius
        self.water = water
        self.pollen = pollen
        self.young_bees = young_bees
        self.p_new_forager = p_new_forager

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