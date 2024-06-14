from __future__ import annotations

import random

from mesa import Agent
from enum import Enum
from typing import Tuple
from math import hypot

from TACABModel.BeeHive import BeeHive
from TACABModel.BeeModel import BeeModel
from TACABModel.Resource import Resource

# References:
# [1] J. Rivière et al., “Toward a Complete Agent-Based Model of a Honeybee Colony,” in Highlights of Practical Applications of Agents, Multi-Agent Systems, and Complexity: The PAAMS Collection, J. Bajo, J. M. Corchado, E. M. Navarro Martínez, E. Osaba Icedo, P. Mathieu, P. Hoffa-Dąbrowska, E. del Val, S. Giroux, A. J. M. Castro, N. Sánchez-Pi, V. Julián, R. A. Silveira, A. Fernández, R. Unland, and R. Fuentes-Fernández, Eds., Cham: Springer International Publishing, 2018, pp. 493–505. doi: 10.1007/978-3-319-94779-2_42.

class Bee(Agent):

    # Type-annotated class attribtues
    id: int
    model: BeeModel
    pos: Tuple[float, float]

    hive: BeeHive
    state: Bee.State

    tired: bool

    # Class constants
    SPEED: float = 1.29     # [m/s] as used in [1]

    # Subclass enumerator for denoting bee's current activity
    class State(Enum):
        IDLE = "idle"           # resting in hive, not interested in foraging
        READY = "ready"         # in the hive, ready to forage
        FORAGING = "foraging"   # scouting ot stricly foraging due to recruitment

    # Initializer and methods
    def __init__(self: Bee, id: int, model: BeeModel, hive: BeeHive):
        super().__init__(id, model)
        self.hive = hive
        self.pos = hive.pos
        self.state = Bee.State.IDLE

        self.tired = False

    def is_foraging(self):
        return self.state == Bee.State.FORAGING

    def new_position(self):
        dx = random.uniform(0, Bee.SPEED) * (1 if random.random() < 0.5 else -1)
        dy = hypot(Bee.SPEED, -dx) * (1 if random.random() < 0.5 else -1)

        return (self.pos[0] + dx, self.pos[1] + dy)

    def step(self):
        pass
    
    def try_collect_resources(self):
        x, y = self.location
        neighbors = self.model.space.get_neighbors(self.location, include_center=True, radius=self.interaction_range)
        resource_neighbors = [n for n in neighbors if isinstance(n, Resource)]
        # Make decision which resource to collect
        return