from __future__ import annotations

import random

from mesa import Agent
from enum import Enum
from typing import Tuple
from math import hypot

from TACABModel.BeeHive import BeeHive
from TACABModel.Resource import Resource

# References:
# [1] J. Rivière et al., “Toward a Complete Agent-Based Model of a Honeybee Colony,” in Highlights of Practical Applications of Agents, Multi-Agent Systems, and Complexity: The PAAMS Collection, J. Bajo, J. M. Corchado, E. M. Navarro Martínez, E. Osaba Icedo, P. Mathieu, P. Hoffa-Dąbrowska, E. del Val, S. Giroux, A. J. M. Castro, N. Sánchez-Pi, V. Julián, R. A. Silveira, A. Fernández, R. Unland, and R. Fuentes-Fernández, Eds., Cham: Springer International Publishing, 2018, pp. 493–505. doi: 10.1007/978-3-319-94779-2_42.

class Bee(Agent):

    # Type-annotated class attribtues
    pos: Tuple[float, float]

    hive: BeeHive
    state: Bee.State
    resource: Resource

    tired: bool
    found_source: bool
    dance: bool
    recruited: bool
    ready_timeout: bool

    ready_for: int
    tired_for: int
    num_bees_listening: int
    outside_for: int

    # Class constants
    FLIGHT_SPEED: float = 1.29                  # [m/s] as used in [1]
    NECTAR_CONSUMED_IN_FLIGHT: float = 0.0083   # [mg/m] as used in [1]
    NECTAR_FULL_MIN: float = 14.6               # [mg] as defined in [1]
    NECTAR_FULL_MAX: float = 16.0               # [mg] as defined in [1]
    READY_TIME_MAX: int = 30*60                 # [s] as defined in [1]

    P_DEATH: float = 0.0                        # as defined in [1]
    P_FULL_RETURN_SCOUT: float = 0.43           # as defined in [1]
    P_FULL_RETURN_RECRUITED: float = 0.93       # as defined in [1]
    P_DANCEFLOOR: float = 0.001                 # as defined in [1]
    P_SCOUT: float = 0.00825                    # as defined in [1]
    
    P_TIRED: float = 0.001                      # my own adaptation
    TIRED_MIN: int = 15*60                      # [s], my own adaptation
    TIRED_MAX: int = 60*60                      # [s], my own adaptation

    MIN_GO_OUT_TEMP: float = 11.0               # as defined in [1]
    MAX_GO_OUT_TEMP: float = 40.0               # as defined in [1]

    # Subclass enumerator for denoting bee's current activity
    class State(Enum):
        RESTING = "resting"           # in the hive, resting & not interested in foraging
        DANCEFLOOR = "dancefloor"     # in the hive, on the dancefloor
        READY = "ready"               # in the hive, ready to forage
        RECRUITING = "recruiting"     # in the hive, recruiting other bees to forage
        FULL_RETURN = "full_return"   # returned from foraging with resources (success)
        EMPTY_RETURN = "empty_return" # returned from foraging without resources (no success)
        SCOUTING = "scouting"         # scouting for resources as a result of spontaneous "decision"
        FORAGING = "foraging"         # foraging for resources as a result of recruitment

    # Initializer and methods
    def __init__(self: Bee, id: int, model, hive: BeeHive):
        super().__init__(id, model)
        self.hive = hive
        self.resource = None

        self.pos = hive.pos
        self.state = Bee.State.RESTING

        self.tired = False
        self.found_source = False
        self.dance = False
        self.recruited = False
        self.ready_timeout = False

        self.ready_for = 0
        self.tired_for = 0
        self.num_bees_listening = 0
        self.outside_for = 0

    def new_position(self):
        dx = random.uniform(0, Bee.SPEED) * (1 if random.random() < 0.5 else -1)
        dy = hypot(Bee.SPEED, -dx) * (1 if random.random() < 0.5 else -1)

        return (self.pos[0] + dx, self.pos[1] + dy)

    def step(self):
        if self.state == Bee.State.RESTING:
            # Determine if the bee is still tired
            if self.tired:
                if (self.tired_for <= 0):
                    self.tired = False
                else:
                    self.tired_for -= 1
            # Go on the dancefloor with certain probability
            elif (random.random() < Bee.P_DANCEFLOOR):
                self.state = Bee.State.DANCEFLOOR
        elif self.state == Bee.State.DANCEFLOOR:
            # Becoming tired has priority over anything else
            if (random.random() < Bee.P_TIRED):
                self.tired_for = random.randint(Bee.TIRED_MIN, Bee.TIRED_MAX)
                self.tired = True
                self.state = Bee.State.RESTING
            elif (self.found_source):
                # Determine how many bees could be listening
                # NOTE: Yes, we don't care if there are actually at least 3 bees we could recruit
                self.num_bees_listening = random.randint(0, 3)

                if (self.num_bees_listening > 0):
                    # If there is at least one bee to dance to, start dancing
                    self.dance = True
                else:
                    self.dance = False

                if (self.dance):
                    # If bee which found resources is dancing, it is recruiting
                    self.state = Bee.State.RECRUITING
                else:
                    # Otherwise it goes back to the resource 
                    # NOTE: Perhaps the state should be FORAGING then ?
                    self.state = Bee.State.SCOUTING
            else:
                if (random.random() < Bee.P_SCOUT):
                    # Spontaneous scouting
                    self.state = Bee.State.SCOUTING
                else:
                    # Waiting for recruitment
                    self.state = Bee.State.READY
                    self.ready_time = 0

        elif self.state == Bee.State.READY:
            # Becoming tired has priority over anything else
            if (random.random() < Bee.P_TIRED):
                self.tired_for = random.randint(Bee.TIRED_MIN, Bee.TIRED_MAX)
                self.tired = True
                self.ready_timeout = False
                self.ready_for = 0

                self.state = Bee.State.RESTING
            elif (self.recruited):
                # Became recruited by other bee
                self.state = Bee.State.FORAGING
                self.ready_timeout = False
                self.ready_for = 0
            elif (self.ready_timeout and random.random() < Bee.P_SCOUT):
                # Spontaenous scouting
                self.state = Bee.State.SCOUTING
                self.ready_timeout = False
                self.ready_for = 0
            else:
                # If the bee was waiting ready for too long
                if (self.ready_for > Bee.READY_TIME_MAX):
                    self.ready_timeout = True

                # Increment the time it was being ready and remain in the current state
                self.ready_for += 1
                self.state = Bee.State.READY

        elif self.state == Bee.State.RECRUITING:
            # Recruit other bees
            potential_employees = self.model.get_agents_of_type(Bee)
            potential_employees = list(filter(lambda bee : bee.state != Bee.State.READY, potential_employees))

            if len(potential_employees) > 0:
                employees = random.choices(potential_employees, k = min(self.num_bees_listening, len(potential_employees)))
            else:
                employees = []
            
            steps_to_resource = self.resource.distance // Bee.FLIGHT_SPEED

            for employee in employees:
                employee.resource = self.resource
                employee.recruited = True
                employee.outside_for = steps_to_resource
            
            if (random.random() < Bee.P_TIRED):
                # Forager rests if it became tired
                self.tired_for = random.randint(Bee.TIRED_MIN, Bee.TIRED_MAX)
                self.tired = True
                self.ready_timeout = False
                self.ready_for = 0

                self.state = Bee.State.RESTING
            else:
                # Otherwise it becomes self-recruited
                self.recruited = True
                self.state = Bee.State.FORAGING

        elif self.state == Bee.State.FULL_RETURN:
            # Store the nectar brought from the trip
            self.hive.nectar_stock += random.uniform(Bee.NECTAR_FULL_MIN, Bee.NECTAR_FULL_MAX)
            # Go back on the dancefloor
            self.state = Bee.State.DANCEFLOOR
        elif self.state == Bee.State.EMPTY_RETURN:
            # Go back on the dancefloor
            self.state = Bee.State.DANCEFLOOR
        elif self.state == Bee.State.SCOUTING:
            if (self.outside_for > 0):
                self.outside_for -= 1
            else:
                if (random.random() < Bee.P_FULL_RETURN_SCOUT):
                    resources = self.model.get_agents_of_type(Resource)
                    profitabilities = [resource.profitability(self.model.day) for resource in resources]
                    self.resource = random.choices(resources, weights=profitabilities, k=1)[0]

                    self.found_source = True
                    self.state = Bee.State.FULL_RETURN
                else:
                    self.state = Bee.State.EMPTY_RETURN

        elif self.state == Bee.State.FORAGING:
            if (random.random() < Bee.P_FULL_RETURN_RECRUITED):
                    self.state = Bee.State.FULL_RETURN
            else:
                self.state = Bee.State.EMPTY_RETURN