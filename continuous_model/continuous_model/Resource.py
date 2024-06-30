from __future__ import annotations
from enum import Enum
from typing import Tuple
import math

from mesa import Agent, Model

from .config import ResourceConfig


class ResourceType(Enum):
    NECTAR = "nectar"

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
        if self.quantity <= 0:
            self.quantity = 0
            self.radius = 0
        else:
            self.radius = math.sqrt(self.quantity / ResourceConfig.DEFAULT_QUANTITY) * ResourceConfig.DEFAULT_RADIUS

        if not self.persistent and self.quantity <= 0:
            # TODO: Mesa provides functionality to do that more efficiently
            self.pos = None
            self.model.n_agents_existed -= 1
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
            self.model.agents.remove(self) # All agents maintained in scheduler
            self.remove()



    def extraction(self,bee_carrying_capacity):         
        if self.persistent == True:
            return bee_carrying_capacity
        else:
            self.quantity -= bee_carrying_capacity
        return bee_carrying_capacity

            # TODO: Manage the fact that bees are trying to go to a removed resource
            # self.model.kill_agents.append(self)