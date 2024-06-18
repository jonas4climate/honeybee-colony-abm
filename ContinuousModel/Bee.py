from __future__ import annotations

from mesa import Agent, Model
from enum import Enum
from typing import Tuple

from ContinuousModel.Hive import Hive

class Bee(Agent):

    # Bee's current activity
    class State(Enum):
        RESTING = "resting"
        EXPLORING = "exploring"
        CARRYING = "carrying"
        DANCING = "dancing"
        FOLLOWING = "following"

    # Class constants / fixed parameters
    FIELD_OF_VIEW = 20

    # Class properties
    id: int                         # unique identifier, required in mesa package
    model: Model                    # model the agent belongs to

    hive: Hive                      # the Hive the Bee agent belongs to
    location: Tuple[int, int]       # agent's current position, x and y coordinate

    state: Bee.State                # Bee's current activity
    wiggle: bool                    # whether the Bee agent is currently wiggle dancing

    age: float                      # agent's current age (which has influence on their activity)
    fov: float                      # radius around the agent in which it can perceive the environment
    health: float                   # agent's health status

    # Class methods
    def __init__(self, id, model, hive, fov=FIELD_OF_VIEW, age=0, health=1.0, state=State.RESTING, wiggle=False):
        super().__init__(id, model)

        self.hive = hive
        self.location = hive.location

        self.state = state
        self.wiggle = wiggle

        self.age = age
        self.fov = fov
        self.health = health
    
    def step(self, dt=1):
        self.step_by_caste(dt)                      # Manage action based on caste
        self.age += dt                              # Manage ageing
        self.manage_death()                         # Manage death

    def step_by_caste(self, dt):
        if self.state == Bee.State.RESTING:
            # 1. Might perceive low resources at beehive -> and change to EXPLORING
            pass
            # 2. Otherwise, does random walk around beehive 
            pass

        if self.state == Bee.State.EXPLORING:
            # 1. Might abort
            pass
            # 2. Might perceive WIGGLEDANCE -> and change do FOLLOW!
            # TODO: Incorporate weather so bees FOV is reduced
            real_fov = self.fov*0.5
            pass
            # 3. If not, it does random walk, biased towards resources and bee trails
            pass

        if self.state == Bee.State.CARRYING:
            # 1. At first, spends some time gathering the resource without moving
            # This can be done by waiting for specific time or adding a GATHERING state
            pass
            # 2. Leaves some trail on its location
            # TODO: Incorporate weather so bees that are not Resting have increased chance of dying!
            pass

            # 3. Does random walk, heavily biased towards self.BeeHive.location
            # Alternatively, heads in straight line there
            pass
            # 4. On reaching the beeHive, deposit resources and switch to DANCING
        
        if self.state == Bee.State.DANCING:
            # 1. Does dance for some time, setting its self.waggle to True
            pass
            # 2. After some time, goes to RESTING
            pass

        if self.state == Bee.State.FOLLOWING:
            # 1. First, it reads the resource direction from the other bee
            pass
            # 2. Then, it heads in that direction for some fixed time
            pass
            # 3. Then, switch to EXPLORING
            pass

    def manage_death(self):
        # TODO: Incorporate weather so bees that are not Resting have increased chance of dying!

        # death = False
        # if self.health <= 0: # Death by health
        #     death = True
        # if self.max_age is not None and self.age >= self.max_age: # Death by age
        #     death = True

        # if death:
        #     self.model.space.remove_agent(self)
        #     self.model.schedule.remove(self)
        return