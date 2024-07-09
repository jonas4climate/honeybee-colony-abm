from __future__ import annotations
from enum import Enum
from typing import Tuple
import math

from mesa import Agent, Model

from ..util.BeeState import BeeState
from ..config.ResourceConfig import ResourceConfig as RC

class Resource(Agent):

    def __init__(
            self, 
            model: 'Model',
            quantity: float = None,
        ):
        super().__init__(model.next_id(), model)

        # Hive's position in space, initialization done through ContinousSpace.place_agent()
        self.pos = None

        # Quantity of nectar available at the resource
        if quantity == None:
            self.quantity = self.model.resource_config.DEFAULT_QUANTITY
        else:
            self.quantity = quantity
            
        assert self.quantity // self.model.bee_config.CARRYING_CAPACITY

    def step(self):
        """Agent's step function required by Mesa package."""
        nearby_foragers = self.model.space.get_neighbors(self.pos, RC.RADIUS, include_center=False)
        nearby_foragers = list(filter(lambda agent : self.model.is_bee(agent), nearby_foragers))
        nearby_foragers = list(filter(lambda bee : (bee.is_exploring or bee.is_following), nearby_foragers))

        # Each nearby forager extracts the resource
        for forager in nearby_foragers:
            if (self.quantity == 0):
                # If there is no resource to take, the bee returns with empty hands
                forager.state = BeeState.RETURNING
            else:
                # Otherwise it grabs the resource and goes back to the hive with the information where the resource is
                self.quantity = max(0, self.quantity - self.model.bee_config.CARRYING_CAPACITY)
                forager.state = BeeState.CARRYING
                forager.resource_destination = self