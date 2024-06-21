from mesa import Agent
from numpy.random import normal

from set_parameters import NECTAR_QUANTITY, NECTAR_SD, CARRY_CAPACITY


class Resource(Agent):
    def __init__(self, model, location, persistent=True):
        super().__init__(model.next_id(), model)
        self.steps = 0
        self.location = location
        self.persistent = persistent  # `True` : resource lasts forever
        self.remaining_nectar = abs(normal(NECTAR_QUANTITY, NECTAR_SD))
        # self.type = type  # "honey", "water",...
        # self.quantity = quantity  # [0,1]

    def get_nectar(self):
        if self.persistent:
            pass
        else:
            self.remaining_nectar -= CARRY_CAPACITY

    def enough_nectar(self):
        return self.remaining_nectar > CARRY_CAPACITY

    def step(self):
        self.steps += 1
