from __future__ import annotations
from enum import Enum
from typing import Tuple
import math

from mesa import Agent, Model

class ResourceType(Enum):
    NECTAR = "nectar"

class Resource(Agent):
    def __init__(
            self, 
            model: 'Model',
            resource_type: ResourceType = ResourceType.NECTAR
        ):
        super().__init__(model.next_id(), model)
        self.pos = None  # agent's current position, x and y coordinate
        self.type = resource_type  # type of the resource
        resource_config = model.resource_config
        self.quantity = resource_config.default_quantity  # (in kg) how much of the resource is left
        self.default_quantity = resource_config.default_quantity
        self.radius = resource_config.default_radius  # (in m) effective radius of the resource
        self.default_radius = resource_config.default_radius
        self.persistent = resource_config.default_persistent  # whether the resource persists forever
        self.nectar_production_rate = resource_config.nectar_production_rate
        
    def step(self):
        self.produce_nectar()
        # 1. Depletion, if quantity reaches 0
        # self.radius = self.quantity / ResourceConfig.DEFAULT_QUANTITY * ResourceConfig.DEFAULT_RADIUS
        if self.quantity <= 0:
            self.quantity = 0
            self.radius = 0
        else:
            self.radius = math.sqrt(self.quantity / self.default_quantity) * self.default_radius

        if not self.persistent and self.quantity <= 0:
            # TODO: Mesa provides functionality to do that more efficiently
            self.pos = None
            self.model.n_agents_existed -= 1
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
            self.model.agents.remove(self) # All agents maintained in scheduler
            self.remove()

    def produce_nectar(self):
        self.quantity += self.nectar_production_rate*self.model.dt

            # TODO: Manage the fact that bees are trying to go to a removed resource
            # self.model.kill_agents.append(self)