from __future__ import annotations

from mesa import Agent
from typing import Tuple

from TACABModel.BeeModel import BeeModel

class Resource(Agent):
    id: int
    model: BeeModel

    pos: Tuple[float, float]

    def __init__(self: Resource, id: int, model: BeeModel, pos: Tuple[int, int]):
        super().__init__(id, model)
        self.pos = pos
        
        # TODO: Complete

    def step(self):
        # Should replentish or go extinct if quantity reaches 0
        pass    