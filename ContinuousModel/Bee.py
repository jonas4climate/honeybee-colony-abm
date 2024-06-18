# import mesa
from mesa import Agent
# from mesa.space import ContinuousSpace
# from mesa.datacollection import DataCollector
from enum import Enum


class State(Enum):
    RESTING = "resting"
    EXPLORING = "exploring"
    CARRYING = "carrying"
    DANCING = "dancing"
    FOLLOWING = "following"

class Bee(Agent):
    def __init__(self, id, model, age, fov, health, BeeHive, location, state, wiggle):
        super().__init__(id, model)
        self.age = age                           # Float: Age of forager bee
        self.fov = fov                              # Float: Radius of vision    
        self.health = health                        # Float: [0,1]
        self.hive = BeeHive                         # Hive: the hive the bee belongs to    
        self.location = location                    # Tuple: (x,y)
        self.state = state
        self.wiggle = wiggle                        # Bool: Whether the bee is wiggle dancing
    
    def step(self, dt=1):
        self.step_by_caste(dt)                      # Manage action based on caste
        self.age += dt                              # Manage ageing
        self.manage_death()                         # Manage death

    def step_by_caste(self, dt):
        if self.state == State.RESTING:
            # 1. Might perceive low resources at beehive -> and change to EXPLORING
            pass
            # 2. Otherwise, does random walk around beehive 
            pass

        if self.state == State.EXPLORING:
            # 1. Might abort
            pass
            # 2. Might perceive WIGGLEDANCE -> and change do FOLLOW!
            # TODO: Incorporate weather so bees FOV is reduced
            real_fov = self.fov*0.5
            pass
            # 3. If not, it does random walk, biased towards resources and bee trails
            pass

        if self.state == State.CARRYING:
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
        
        if self.state == State.DANCING:
            # 1. Does dance for some time, setting its self.waggle to True
            pass
            # 2. After some time, goes to RESTING
            pass

        if self.state == State.FOLLOWING:
            # 1. First, it reads the resource direction from the other bee
            pass
            # 2. Then, it heads in that direction for some fixed time
            pass
            # 3. Then, switch to EXPLORING
            pass

    def manage_death(self):
        # TODO: Incorporate weather so bees that are not Resting have increased chance of dying!

        death = False
        if self.health <= 0: # Death by health
            death = True
        if self.max_age is not None and self.age >= self.max_age: # Death by age
            death = True

        if death:
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
        return