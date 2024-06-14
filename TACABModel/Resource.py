from __future__ import annotations

from mesa import Agent
from typing import Tuple
from numpy import pi, sqrt, exp

from TACABModel.BeeModel import BeeModel

class Resource(Agent):
    # Type-annotated class attribtues
    id: int
    model: BeeModel

    pos: Tuple[float, float]
    radius: float

    distance: float
    duration: float
    peak: float
    sugar_concentration: float

    def __init__(self: Resource, id: int, model: BeeModel, 
                 pos: Tuple[int, int], radius: float,
                 distance: float, duration: float, peak: float, sugar_concentration: float):
        super().__init__(id, model)
        self.pos = pos
        self.radius = radius

        self.distance = distance
        self.duration = duration
        self.peak = peak
        self.sugar_concentration = sugar_concentration

    def source_factor(self, nb):
        # Formula adapted from source material
        
        # Renaming some parameters for convenience
        d = self.duration
        p = self.peak

        return 1 - ((1 / ((d / 4) * sqrt(2 * pi))) * exp(-((nb - p)**2 / (d**2 / 2))))
    
    def profitability(self, nb):
        return (self.sugar_concentration) * (1 - self.source_factor(nb)) / self.distance

    def step(self):
        # Should replentish or go extinct if quantity reaches 0
        pass    