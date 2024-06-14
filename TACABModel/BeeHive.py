from __future__ import annotations

from mesa import Agent
from typing import Tuple

from TACABModel.BeeModel import BeeModel

class BeeHive(Agent):
    id: int
    model: BeeModel
    pos: Tuple[float, float]

    def __init__(self: BeeHive, id: int, model: BeeModel, pos: Tuple[int, int]):
        super().__init__(id, model)
        self.pos = pos

    def step(self):
        pass