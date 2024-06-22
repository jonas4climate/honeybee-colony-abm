from __future__ import annotations

from mesa import Agent, Model

from enum import Enum
from typing import Tuple
from math import atan2,cos,sin,sqrt
import numpy as np
from scipy.stats import multivariate_normal

from .Resource import Resource
from .Weather import Weather

class Bee(Agent):

    # Bee's current activity
    class State(Enum):
        RESTING = "resting"
        RETURNING = "returning"
        EXPLORING = "exploring"
        CARRYING = "carrying"
        DANCING = "dancing"
        FOLLOWING = "following"

    # Class constants / fixed parameters
    FIELD_OF_VIEW = 20              # 20 (meters) TODO: calibrate further using real data
    STARVATION_SPEED = 1/(60*60*24) # within 1 day (rate / second) TODO: calibrate further using real data
    MAX_AGE = (60*60*24*7*6)        # within 6 weeks (in seconds) TODO: calibrate further using real data
    P_DEATH_BY_STORM = 1/(60*60)    # on average within 1 hour (probability) TODO: calibrate further
    SPEED = 5                       # 5 (meters / second) 
    PERCEIVE_AS_LOW_FOOD = 2        # (units of food) TODO: calibrate further

    # Class properties
    id: int                         # unique identifier, required in mesa package
    model: Model                    # model the agent belongs to

    #hive: Hive                      # the Hive the Bee agent belongs to
    pos: Tuple[float,float]          # agent's current position

    state: Bee.State                # Bee's current activity
    wiggle: bool                    # whether the Bee agent is currently wiggle dancing

    age: float                      # agent's current age (which has influence on their activity)
    fov: float                      # radius around the agent in which it can perceive the environment
    load:float                      # agent amount of resources its carrying

    # Class methods
    def __init__(self, id, model, hive, location=-1, fov=FIELD_OF_VIEW, age=0, fed=1.0, state=State.RESTING, wiggle=False):
        super().__init__(id, model)

        self.hive = hive

        if location == -1:
            self.pos = hive.pos
        else:
            self.pos = location
    
        self.model.space.place_agent(self, self.pos)

        self.state = state
        self.wiggle = wiggle
        self.wiggle_destiny = None # Location of bee resource once it finds it, which is passed to other bees if wiggle dancing 

        self.age = age
        self.fov = fov
        self.fed = fed
        self.load = 0
    
    def step(self):
        self.step_by_caste()                      # Manage action based on caste
        self.manage_death()                       # Manage death
    
    def resource_attraction(self, pos):
        # TODO: Make it a vectorized operation
        attraction = 0.0
        for resource in self.model.get_agents_of_type(Resource):
            # TODO: Change the covariance value to a reasonable number
            attraction += multivariate_normal.pdf(list(pos), list(resource.pos), cov=self.model.size)
        return attraction

    def move_random_exploration(self):
        """
        Moves randomly in x and y in the interval [-max_movement,max_movement]
        """
        distance = Bee.SPEED*self.model.dt
        # Choose a random point with radius equivalent to speed times time step
        angle = np.random.uniform(0, 2*np.pi)
        dx = distance * np.cos(angle)
        dy = distance * np.sin(angle)

        # Calculate the new position, taking the boundaries into account
        newx = self.pos[0] + dx
        newx = max(-newx, min(self.model.size, newx))

        newy = self.pos[1] + dy
        newy = max(-newy, min(self.model.size, newy))

        newpos = (newx, newy)

        # Calculate resource attraction bias
        # TODO: Use bee STATE to incorporate different biases in random walk!
        # TODO: Positive bias towards the resources
        attraction_current = self.resource_attraction(self.pos)
        attraction_new = self.resource_attraction(newpos)
        
        # TODO: Negative bias away from the hive
        # dist_to_hive = np.hypot(newpos[0] - self.hive.pos[0], newpos[1] - self.hive.pos[1])
        # if dist_to_hive < Bee.HIVE_MOVE_AWAY_TH:

        # Metropolis algorithm
        if attraction_new > attraction_current or np.random.random() < (attraction_new / attraction_current):
            self.model.space.move_agent(self, newpos)
        else:
            # Retry so we ensure the bee moves and doesn't stay still
            self.move_random_exploration()

    def is_close_to_hive(self, threshold=0.1):
        return self.is_close_to(self.hive, threshold)

    def is_resource_close_to_bee(self, resource, threshold=0.1):
        return self.is_close_to(resource, threshold)
    
    def is_close_to(self, agent, threshold):
        distance = sqrt((self.pos[0] - agent.pos[0])**2 + (self.pos[1] - agent.pos[1])**2)
        return distance <= threshold
    
    def move_towards_hive(self):
        self.move_towards(self.hive)

    def move_towards(self, destiny):
        """
        Moves deterministically in straight line towards a target location
        """
        # TODO: Add stochasticity to dx and dy with weather :)
        dx = destiny.pos[0] - self.pos[0]
        dy = destiny.pos[1] - self.pos[1]
        
        distance = (dx**2 + dy**2)**0.5
        move_distance = Bee.SPEED*self.model.dt
        if distance > move_distance:
            angle = atan2(dy, dx)
            new_x = self.pos[0] + move_distance * cos(angle)
            new_y = self.pos[1] + move_distance * sin(angle)
            self.model.space.move_agent(self, (new_x, new_y))
        else:
            self.model.space.move_agent(self, (destiny.x, destiny.y))

    def step_by_caste(self):
        # Bees are resting in the hive until they change their mind and explore
        if self.state == Bee.State.RESTING:
            assert self.load == 0, "Bee cannot be resting and carrying at the same time"
            assert self.wiggle == False, "Bee cannot be resting and wiggle dancing at the same time"
            assert self.wiggle_destiny == None, "Bee cannot be resting and have a wiggle destiny at the same time"
            assert self.is_close_to_hive(), "Bee cannot be resting and not close to hive"

            # 1. Might perceive low resources at beehive -> and change to EXPLORING
            if self.is_close_to_hive() and (self.hive.nectar < Bee.PERCEIVE_AS_LOW_FOOD):
                perceive_low_resources = True
            
            if perceive_low_resources:
                self.state = Bee.State.EXPLORING

        # If bees abort their exploration, they return straight to the hive and start resting
        if self.state == Bee.State.RETURNING:
            if self.is_close_to_hive():
                self.state = Bee.State.RESTING
            else:
                self.move_towards_hive()

        # Bees exploring with random walk if they don't perceive waggle dances
        if self.state == Bee.State.EXPLORING:
            # Might abort with some chance. If not, ight perceive WIGGLEDANCE -> and change do FOLLOW!
            # If not, it does random walk, biased towards resources and bee trails
            ## TODO: increase p_abort dependent on weather
            ## TODO: Make p_follow dependent on weather?
            p_abort = 0.0
            abort = True if np.random.random() < p_abort else False

            if abort:
                self.state = Bee.State.RETURNING
            else:
                bees_in_fov = [other_agent for other_agent in self.model.agents if other_agent != self and ((other_agent.pos[0] - self.pos[0])**2 + (other_agent.pos[1] - self.pos[1])**2)**0.5 <= self.fov and isinstance(other_agent, Bee)]
                for other_bee in bees_in_fov:
                    if other_bee.wiggle:
                        p_follow = 0.8
                        follow_dance = True if np.random.random() < p_follow else False
                        if follow_dance:
                            self.wiggle_destiny = other_bee.wiggle_destiny
                            self.state = Bee.State.FOLLOWING
                            return
                
                # See if there is resource near!
                ## TODO: Add detection of bee close to resource
                resources_in_fov = [resource for resource in self.model.agents if resource != self and ((resource.pos[0] - self.pos[0])**2 + (resource.pos[1] - self.pos[1])**2)**0.5 <= self.fov and isinstance(resource, Resource)]

                for resource in resources_in_fov:
                    if self.is_resource_close_to_bee(resource, threshold=0.05):
                        self.wiggle_destiny = resource.pos
                        self.state = Bee.State.CARRYING
                        return

                # If not, move randomly but biased towards resources and trails
                self.move_random_exploration()



        if self.state == Bee.State.CARRYING:
            # 1. At first, gather resource without moving
            # This can be done by waiting for specific time or adding a GATHERING state
            # TODO: Make p_finish_gathering dependent on weather!
            # TODO: Make load of bee reasonable instead of arbitrary 1
            if self.load == 0:
                self.load = 1

                p_finish_gathering = 0.9
                finish_gathering = True if np.random.random() < p_finish_gathering else False
                if finish_gathering:
                    self.load = 1
            else:
                if self.is_close_to_hive():
                    # TODO: Account for resource type, right now it always deposists nectar
                    self.hive.nectar += self.load
                    self.load = 0
                    self.wiggle = True
                    self.state = Bee.State.DANCING
                else:
                    self.move_towards_hive()
                
        

        if self.state == Bee.State.DANCING:
            # 1. Does dance for some time, setting its self.waggle to True
            # 2. After some time, goes to RESTING
            # TODO: Make it follow fixed time DANCING_TIME
            p_stop_dance = 0.4
            stop_dancing = True if np.random.random() < p_stop_dance else False

            if stop_dancing:
                self.wiggle = False
                self.state = Bee.State.RESTING
            else:
                #self.wiggle should be True, as it was setted in the CARRYING state loop
                # As it wiggles, it Moves randomly or towards hive 50% chance
                p_random_walk = 0.5
                move_randomly = True if np.random.random() < p_random_walk else False
 
                if move_randomly:
                    # TODO: Implement random small movement within the hive
                    pass
                else:
                    self.move_towards_hive()


        if self.state == Bee.State.FOLLOWING:
            # 1. First, it reads the resource direction from the other bee (THIS WAS DONE in the exploring loop)
            # 2. Then, it heads in that direction for some fixed time
            # 3. Then, switch to EXPLORING
            
            # 1 Have we reach destiny already? 
            # self.pos - self.wiggle.destiny isclose
            # If so switch ro carrying

            if self.is_resource_close_to_bee(self.wiggle_destiny, threshold=0.05):
                self.state = Bee.State.CARRYING
                # wiggle_destiny is already set to resource location
            
            p_stop_follow = 0.01 # TODO: instead have it be scale based on distance?
            stop_following = True if np.random.random() < p_stop_follow else False

            if stop_following:
                self.state = Bee.State.EXPLORING
            else:   
                self.move_towards(self.wiggle_destiny)
  
    def manage_death(self):
        self.fed -= Bee.STARVATION_SPEED*self.model.dt
        if self.fed <= 0: # Death by starvation
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
            return
        
        self.age += self.model.dt
        if self.age >= Bee.MAX_AGE: # Death by age
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
            return

        if self.model.weather == Weather.STORM and np.random.random() < Bee.P_DEATH_BY_STORM*self.model.dt:
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
            return