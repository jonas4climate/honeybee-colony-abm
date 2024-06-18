"""
This file contains the BeeHive class.
"""
from mesa import Agent
from set_parameters import REPRODUCTION
from Bee import Bee
from random import random

class BeeHive(Agent):
    def __init__(self, id, model, location):
        super().__init__(id, model)
        self.location = location                    # (x,y) tuple
        self.num_bees = 0                           # Integer: number of bees in the hive
        self.resources = 0                          # Integer: amount of food in the hive
        self.consume = 1                            # Integer: amount of food consumed by bees per day
        self.reproduce_rate = REPRODUCTION


    def store_food(self):
        # TODO: Hive remembers the food location
        self.resources += 1

    def step(self):
        self.num_bees = self.model.schedule.get_agent_count(Bee)

        if random() < self.reproduce_rate:
            self.model.add_bee(self)


