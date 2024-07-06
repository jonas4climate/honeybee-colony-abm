from __future__ import annotations
from enum import Enum
from typing import Tuple
import math

from mesa import Agent, Model

class Resource(Agent):
    def __init__(
            self, 
            model: 'Model',
            location: Tuple[int, int]
        ):
        super().__init__(model.next_id(), model)

        # Resource's position in space
        self.pos = location

        # Reference to the set of parameters governing Resource's agent behaviour
        resource_config = model.resource_config

        # Quantity of nectar available at the resource
        self.quantity = resource_config.default_quantity

        # Radius of the resource, in that proximity it can be foraged
        self.radius = resource_config.default_radius

        # Default radius of the resource in model parameters
        self.default_radius = resource_config.default_radius

    def step(self):
        """Agent's step function required by Mesa package."""
        # Replenish the resources
        # TODO: ?

    def _remove_agent(self):
        """Helper for removing agents."""
        self.pos = None
        self.model.n_agents_existed -= 1
        self.model.space.remove_agent(self)
        self.model.schedule.remove(self)
        self.model.agents.remove(self)
        self.remove()