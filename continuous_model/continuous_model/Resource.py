from __future__ import annotations

from mesa import Agent, Model
from enum import Enum

from typing import Tuple

class Resource(Agent):

    # Type of resource
    class Type(Enum):
        NECTAR = "nectar"
        WATER = "water"
        POLLEN = "pollen"

    # Class properties
    id: int                         # unique identifier, required in mesa package
    model: Model                    # model the agent belongs to

    pos: Tuple[int, int]       # agent's current position, x and y coordinate
    type: Resource.Type             # type of the resource

    quantity: float                 # how much of the resource is left
    radius: float                   # effective radius of the resource
    persistent: bool                # whether the resource persists forever

    # Class methods
    def __init__(self, id, model, location, type=Type.NECTAR, quantity=1.0, radius=50.0, persistent=True):
        super().__init__(id, model)
        
        self.pos = location
        self.type = type

        self.quantity = quantity
        self.radius = radius
        self.persistent = persistent
        
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