from __future__ import annotations
from enum import Enum
from typing import Tuple
import math

from mesa import Agent, Model

from ..agents.BeeSwarm import BeeSwarm, BeeState

class Resource(Agent):

    RADIUS = 10

    def __init__(
            self, 
            model: 'Model',
            location: Tuple[int, int]
        ):
        super().__init__(model.next_id(), model)

        # Resource's position in space
        self.pos = location

        # Quantity of nectar available at the resource
        self.quantity = self.model.resource_config.default_quantity
        assert self.quantity // BeeSwarm.CARRYING_CAPACITY

    def step(self):
        """Agent's step function required by Mesa package."""
        nearby_foragers = self.model.space.get_neighbors(self.pos, Resource.RADIUS, include_center=False)
        nearby_foragers = list(filter(lambda bee : isinstance(bee, BeeSwarm) and bee.is_exploring or bee.is_following, nearby_foragers))

        # Each nearby forager extracts the resource
        for forager in nearby_foragers:
            if (self.quantity == 0):
                # If there is no resource to take, the bee returns with empty hands
                forager.state = BeeState.RETURNING
            else:
                # Otherwise it grabs the resource and goes back to the hive
                self.quantity = max(0, self.quantity - BeeSwarm.CARRYING_CAPACITY)
                forager.state = BeeState.CARRYING