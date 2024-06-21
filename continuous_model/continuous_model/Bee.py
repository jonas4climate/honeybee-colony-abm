from __future__ import annotations

from mesa import Agent, Model
from enum import Enum
from typing import Tuple
from random import uniform, random
from math import atan2,cos,sin,sqrt

#from ContinuousModel.Hive import Hive               # Should not need this import to avoid circular import, its only used in suggestion for class property type
from continuous_model.Resource import Resource

def move_random(bee,max_movement=0.2):
    """
    Moves randomly in x and y in the interval [-max_movement,max_movement]
    """
    print('MOVE RANDOM')
    # TODO: Use bee STATE to incorporate different biases in random walk!
    x = bee.pos[0] + uniform(-max_movement,max_movement)
    y = bee.pos[1] + uniform(-max_movement,max_movement)
    
    # Bound to model region [-size,size]
    x = max(-x, min(bee.model.size, x))
    y = max(-y, min(bee.model.size, y))

    return (x,y)


def move_towards_hive(self, speed=1):
        """
        Moves deterministically in straight line towards a target location
        """
        # TODO: Add stochasticity to dx and dy with weather :)
        dx = self.hive.pos[0] - self.pos[0]
        dy = self.hive.pos[1] - self.pos[1]
        
        distance = (dx**2 + dy**2)**0.5
        if distance > speed:
            angle = atan2(dy, dx)
            new_x = self.pos[0] + speed * cos(angle)
            new_y = self.pos[1] + speed * sin(angle)
            self.model.space.move_agent(self, (new_x, new_y))
        else:
            self.model.space.move_agent(self, (self.hive.pos[0], self.hive.pos[1]))

def is_close_to_hive(self, threshold=0.1):
    distance = sqrt((self.pos[0] - self.hive.pos[0])**2 + (self.pos[1] - self.hive.pos[1])**2)
    return distance <= threshold

def is_resource_close_to_bee(self, resource, threshold):
    distance = sqrt((self.pos[0] - resource.pos[0])**2 + (self.pos[1] - resource.pos[1])**2)
    return distance <= threshold


def move_towards(self, destiny, speed=1):
        """
        Moves deterministically in straight line towards a target location
        """
        # TODO: Add stochasticity to dx and dy with weather :)
        dx = destiny.pos[0] - self.pos[0]
        dy = destiny.pos[1] - self.pos[1]
        
        distance = (dx**2 + dy**2)**0.5
        if distance > speed:
            angle = atan2(dy, dx)
            new_x = self.pos[0] + speed * cos(angle)
            new_y = self.pos[1] + speed * sin(angle)
            self.model.space.move_agent(self, (new_x, new_y))
        else:
            self.model.space.move_agent(self, (destiny.x, destiny.y))



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

    #hive: Hive                      # the Hive the Bee agent belongs to
    pos: Tuple[float,float]
    #x: float                        # agent's current position, x and y coordinate (have to be separated into x and y!)
    #y: float

    state: Bee.State                # Bee's current activity
    wiggle: bool                    # whether the Bee agent is currently wiggle dancing

    age: float                      # agent's current age (which has influence on their activity)
    fov: float                      # radius around the agent in which it can perceive the environment
    health: float                   # agent's health status
    load:float                      # agent amount of resources its carrying
    wiggle_destiny:Tuple[float,float]      # Location of bee resource once it finds it, which is passed to other bees when wiggle dancing 

    # Class methods
    def __init__(self, id, model, hive, location=-1, fov=1, age=0, health=1.0, state=State.RESTING, wiggle=False):
        super().__init__(id, model)

        self.hive = hive

        if location == -1:
            self.pos = hive.pos
        else:
            self.pos = location
    
        self.model.space.place_agent(self, self.pos)

        self.state = state
        self.wiggle = wiggle

        self.age = age
        self.fov = fov
        self.health = health
        self.load = 0
    
    def step(self, dt=1):
        self.step_by_caste(dt)                      # Manage action based on caste
        self.age += dt                              # Manage ageing
        self.manage_death()                         # Manage death

    def step_by_caste(self, dt):
        # TODO: Use dt

        if self.state == Bee.State.RESTING:
            # 1. Might perceive low resources at beehive -> and change to EXPLORING
            # 2. Otherwise, does random walk around beehive
            ## TODO: Add constraint that hive should be in FOV
            ## TODO: Add reasonable low resource limit to start exploring instead of arbitrary 2
            ## TODO: Make random walk biased towards hive
            low_resources = self.hive.nectar < 2 or self.hive.water < 2 or self.hive.nectar <2
            
            #print('Bee resting',low_resources)

            if low_resources:
                self.state = Bee.State.EXPLORING
            else:
                move_random(self,0.01)



        if self.state == Bee.State.EXPLORING:
            # Might abort with some chance. If not, ight perceive WIGGLEDANCE -> and change do FOLLOW!
            # If not, it does random walk, biased towards resources and bee trails
            ## TODO: Make p_abort dependent on weather
            ## TODO: Make p_follow dependent on weather
            p_abort = 0.2
            abort = True if random() < p_abort else False

            if abort:
                self.state = Bee.State.RESTING
            else:
                bees_in_fov = [other_agent for other_agent in self.model.agents if other_agent != self and ((other_agent.pos[0] - self.pos[0])**2 + (other_agent.pos[1] - self.pos[1])**2)**0.5 <= self.fov and isinstance(other_agent, Bee)]
                for other_bee in bees_in_fov:
                    if other_bee.wiggle:
                        p_follow = 0.8
                        follow_dance = True if random() < p_follow else False
                        if follow_dance:
                            self.wiggle_destiny = other_bee.wiggle_destiny
                            self.state = Bee.State.FOLLOWING
                            return
                
                # See if there is resource near!
                ## TODO: Add detection of bee close to resource
                resources_in_fov = [resource for resource in self.model.agents if resource != self and ((resource.pos[0] - self.pos[0])**2 + (resource.pos[1] - self.pos[1])**2)**0.5 <= self.fov and isinstance(resource, Resource)]

                for resource in resources_in_fov:
                    if is_resource_close_to_bee(self,resource,threshold=0.05):
                        self.wiggle_destiny = (resource.x,resource.y)
                        self.state = Bee.State.CARRYING
                        return

                # If not, move randomly but biased towards resources and trails
                self.pos = move_random(self,0.4)



        if self.state == Bee.State.CARRYING:
            # 1. At first, spends some time gathering the resource without moving
            # This can be done by waiting for specific time or adding a GATHERING state
            # For now, its done with random chance
            # TODO: Make p_finish_gathering dependent on weather!
            # TODO: Make load of bee reasonable instead of arbitrary 1
            if self.load == 0:

                p_finish_gathering = 0.9
                finish_gathering = True if random() < p_finish_gathering else False
                if finish_gathering:
                    self.load = 1
            else:
                # 2. Leaves some trail on its location
                ## TODO: Add trail
                ## TODO: Incorporate weather so bees that are not Resting have increased chance of dying!
                pass

                # 4. On reaching the beeHive, deposit resources and switch to DANCING
                if is_close_to_hive(self,threshold=0.1):
                    # TODO: Account for resource type, right now it always deposists nectar
                    self.hive.nectar += self.load
                    self.load = 0
                    self.wiggle = True
                    self.state = Bee.State.DANCING
                else:
                    # If not on beehive yet, does random walk, heavily biased towards self.BeeHive.pos
                    # Alternatively, heads in straight line there
                    move_towards_hive(self, speed=1)
                
        

        if self.state == Bee.State.DANCING:
            # 1. Does dance for some time, setting its self.waggle to True
            # 2. After some time, goes to RESTING
            # TODO: Make it follow a more sensible distribution
            p_stop_dance = 0.4
            stop_dancing = True if random() < p_stop_dance else False

            if stop_dancing:
                self.wiggle = False
                self.state = Bee.State.RESTING
            else:
                #self.wiggle should be True, as it was setted in the CARRYING state loop
                # As it wiggles, it Moves randomly or towards hive 50% chance
                p_random_walk = 0.5
                move_randomly = True if random() < p_random_walk else False
 
                if move_randomly:
                    move_random(self,0.01)
                else:
                    move_towards_hive(self)


        if self.state == Bee.State.FOLLOWING:
            # 1. First, it reads the resource direction from the other bee (THIS WAS DONE in the exploring loop)
            # 2. Then, it heads in that direction for some fixed time
            # 3. Then, switch to EXPLORING
            p_stop_follow = 0.4
            stop_following = True if random() < p_stop_follow else False

            if stop_following:
                self.state = Bee.State.EXPLORING
            else:              
                move_towards(self, self.wiggle_destiny, speed=1)
  
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