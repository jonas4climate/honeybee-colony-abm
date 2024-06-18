from __future__ import annotations

from mesa import Agent
from enum import Enum

class Resource(Agent):

    # Type of reosurce
    class Type(Enum):
        NECTAR = "nectar"
        WATER = "water"
        POLLEN = "pollen"

    def __init__(self, id, model, location, type=Type.NECTAR, quantity=1.0, radius=50.0, persistent=True):
        super().__init__(id, model)
        self.location = location                    # (x,y) tuple
        self.type = type                            # "honey", "water",... # TODO: Implement a separate enum type
        self.quantity = quantity                    # Float: [0,1]
        self.radius = radius                        # Float: effective radius of the resource
        self.persistent = persistent                # Bool: True if resource lasts forever
        
        def step(self):
            # 1. Depletion, if quantity reaches 0
            if not self.persistent and self.quantity <= 0:
                self.model.schedule.remove(self)

        def get_type(self):
            # 1. First method called by bees to extract the resource
            return self.type

        def extraction(self,bee_carrying_capacity):
            # 2. Second method called by bees to extract the resource            
            if self.persistent == True:
                return bee_carrying_capacity
            elif quantity <= bee_carrying_capacity:
                return quantity
            else:
                quantity -= bee_carrying_capacity
                return bee_carrying_capacity