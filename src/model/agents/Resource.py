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

        # Default quantity in model parameters
        self.default_quantity = resource_config.default_quantity

        # Radius of the resource, in that proximity it can be foraged
        self.radius = resource_config.default_radius

        # Default radius of the resource in model parameters
        self.default_radius = resource_config.default_radius

        # Whether the resource can be depleted or persists forever
        self.persistent = resource_config.default_persistent

        # Rate of replenishing nectar level
        # TODO: Remove this, jesus. This is so stupid.
        self.nectar_production_rate = resource_config.nectar_production_rate
        self.extracted_nectar = 0  # (in kg) how much nectar has been extracted from the resource

    def step(self):
        """Agent's step function required by Mesa package."""
        # Replenish the resources
        self.produce_nectar()
        
        # TODO: Remove this, jesus. This is soooo stupid.
        if self.quantity <= 0:
            self.quantity = 0
            self.radius = 0
        else:
            self.radius = math.sqrt(self.quantity / self.default_quantity) * self.default_radius

    def produce_nectar(self):
        """Replenish the nectar by a fixed value given in model parameters."""
        self.quantity += self.nectar_production_rate*self.model.dt

    def _remove_agent(self):
        """Helper for removing agents."""
        self.pos = None
        self.model.n_agents_existed -= 1
        self.model.space.remove_agent(self)
        self.model.schedule.remove(self)
        self.model.agents.remove(self)
        self.remove()