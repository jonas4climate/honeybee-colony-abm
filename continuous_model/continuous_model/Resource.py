from __future__ import annotations
from enum import Enum
from typing import Tuple

from mesa import Agent, Model

from .config import ResourceConfig


class ResourceType(Enum):
    NECTAR = "nectar"
    WATER = "water"
    POLLEN = "pollen"


class Resource(Agent):
    def __init__(
            self, 
            model: 'Model', 
            location: Tuple[int, int], 
            resource_type: ResourceType = ResourceType.NECTAR, 
            quantity: float = ResourceConfig.DEFAULT_QUANTITY, 
            radius: float = ResourceConfig.DEFAULT_RADIUS,
            persistent: bool = ResourceConfig.DEFAULT_PERSISTENT
        ):
        super().__init__(model.next_id(), model)
        self.pos = location  # agent's current position, x and y coordinate
        self.type = resource_type  # type of the resource
        self.quantity = quantity  # (in kg) how much of the resource is left
        self.radius = radius  # (in m) effective radius of the resource
        self.persistent = persistent  # whether the resource persists forever
        
    def step(self):
        # 1. Depletion, if quantity reaches 0
        # self.radius = self.quantity / ResourceConfig.DEFAULT_QUANTITY * ResourceConfig.DEFAULT_RADIUS
        self.radius -= 1
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