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
    # id: int                         # unique identifier, required in mesa package
    model: Model                    # model the agent belongs to

    pos: Tuple[int, int]       # agent's current position, x and y coordinate
    type: Resource.Type             # type of the resource

    quantity: float                 # (in kg) how much of the resource is left
    radius: float                   # (in m) effective radius of the resource
    persistent: bool                # whether the resource persists forever

    # Class methods
    def __init__(self, model, location, type=Type.NECTAR, quantity=0.1, radius=50.0, persistent=False):
        super().__init__(model.next_id() , model)
        
        self.pos = location
        self.type = type

        self.quantity = quantity
        self.radius = radius
        self.persistent = persistent
        
    def step(self):
        # 1. Depletion, if quantity reaches 0
        if not self.persistent and self.quantity <= 0:
            # TODO: Mesa provides functionality to do that more efficiently
            self.model.n_agents_existed -= 1
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
            # self.model.agents.remove(self) # All agents maintained in scheduler
            self.remove()
            # self.model.kill_agents.append(self)

    def get_type(self):
        # 1. First method called by bees to extract the resource
        return self.type

    def extraction(self,bee_carrying_capacity):
        # 2. Second method called by bees to extract the resource            
        if self.persistent == True:
            return bee_carrying_capacity
        elif self.quantity <= bee_carrying_capacity:
            return self.quantity
        else:
            self.quantity -= bee_carrying_capacity
            return bee_carrying_capacity