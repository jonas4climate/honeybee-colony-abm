"""
This file contains the BeeHive class.
"""

from random import random

from mesa import Agent

from Bee import Bee
from set_parameters import REPRODUCTION_RATE, CONSUME_RATE, NECESSORY_FOOD, NECTAR_NEEDED


class BeeHive(Agent):
    def __init__(self, model, location):
        super().__init__(model.next_id(), model)
        self.model = model
        self.location = location  # (x,y) tuple
        self.num_bees = 0  # Integer: number of bees in the hive
        self.nectar = 0  # Integer: amount of nectar in the hive
        self.consume = CONSUME_RATE  # Integer: amount of food consumed by bees per day
        self.reproduce_rate = REPRODUCTION_RATE
        self.food = 20
        self.necessary_food = NECESSORY_FOOD
        self.nectar_needed = NECTAR_NEEDED

    def store_nectar(self):
        # TODO: Hive remembers the food location
        self.nectar += 1

    def kill_hive(self):
        return self.food < self.necessary_food

    def step(self):
        """
        1. Make food from nectar
        2. Feed bees
        3. Check if enough food, otherwise die
        4. Reproduce

        """
        self.num_bees = self.model.schedule.get_agent_count(Bee)

        if self.nectar >= self.nectar_needed:
            self.food += 1
            self.nectar = 0

        self.food -= CONSUME_RATE

        if random() < self.reproduce_rate:
            self.model.add_baby(self)
            self.num_bees += 1






