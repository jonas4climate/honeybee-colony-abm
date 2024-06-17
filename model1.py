"""
Model 1
Jonas, Bartek and Pablo
Based on the PDF Pablo sent on Saturday.
"""

import mesa
from mesa import Agent, Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
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
    





class BeeHive(Agent):
    def __init__(self, id, model, location, radius, water, pollen, young_bees, p_new_forager):
        super().__init__(id, model)
        self.location = location
        self.radius = radius
        self.water = water
        self.pollen = pollen
        self.young_bees = young_bees
        self.p_new_forager = p_new_forager

    def step(self):
        # 1. Feed bees
        # Get all young ones as well as foragers around beehive
        # Prioritize hunger ones! Turning water and pollen into bee health
        pass

        # 2. Mature bees
        # Use p_new_forager to instantiate bees
        pass
        # Then, update p_new_forager based on young, water, and pollen, and weather!!
        pass

        # 3. Create young bees
        # Based on resources and weather
        pass


class Resource(Agent):
    def __init__(self, id, model, location, type, quantity, persistent):
        super().__init__(id, model)
        self.location = location                    # (x,y) tuple
        self.type = type                            # "honey", "water",...
        self.quantity = quantity                    # Float: [0,1]
        self.persistent = persistent                # Bool: True if resource lasts forever
        
        def step(self):
            # 1. Depletion, if quantity reaches 0
            if not self.persistent and self.quantity <= 0:
                self.model.schedule.remove(self)

        def get_type(self):
            # 1. First method called by bees to extract the resource
            return self.type

        def extraction(self,bee_carrying_capacity):
            # 2. Second method called by bees to extract the resource            
            if self.persistent == True:
                return bee_carrying_capacity
            elif quantity <= bee_carrying_capacity:
                return quantity
            else:
                quantity -= bee_carrying_capacity
                return bee_carrying_capacity