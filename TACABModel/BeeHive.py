from __future__ import annotations

from mesa import Agent
from typing import Tuple

from TACABModel.BeeModel import BeeModel

class BeeHive(Agent):

    # Type-annotated class attribtues
    id: int
    model: BeeModel
    pos: Tuple[float, float]

    nectar_stock: float     # Float in range [0, 1]
    pollen_stock: float     # Float in range [0, 1]

    # Class constants
    RADIUS = 20

    def __init__(self: BeeHive, id: int, model: BeeModel, pos: Tuple[int, int]):
        super().__init__(id, model)
        self.pos = pos

        self.nectar_stock = 0.5
        self.pollen_stock = 0.5

    def step(self):
        pass