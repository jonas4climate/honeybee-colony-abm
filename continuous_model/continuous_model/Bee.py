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
    FIELD_OF_VIEW = 20              # 20 (in m) TODO: calibrate further using real data
    STARVATION_SPEED = 1/(60*60*24) # within 1 day (in rate/s)
    MAX_AGE = (60*60*24*7*6)        # within 6 weeks (in s)
    P_DEATH_BY_STORM = 1/(60*60)    # on average within 1 hour (probability) TODO: calibrate further
    SPEED = 5                       # 5 (in m/s) 
    PERCEIVE_AS_LOW_FOOD = 2        # 2 (in kg) TODO: calibrate further
    DANCING_TIME = 60               # 1 minute (in s) TODO: calibrate further
    P_FOLLOW_WIGGLE_DANCE = 1       # 100% (probability) TODO: calibrate further
    P_ABORT_EXPLORING = 1/(60*60)   # on average within 1 hour (probability) TODO: calibrate further
    P_ABORT_FOLLOWING = 1/(60*60)   # on average within 1 hour (probability) TODO: calibrate further
    STORM_ABORT_FACTOR = 10         # 10 times more likely to abort during storm TODO: calibrate further
    CARRYING_CAPACITY = 0.001       # 1g (in kg) TODO: calibrate further
    GATHERING_RATE = 0.0001         # 0.1g/s (kg/s) TODO: calibrate further

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

        self.pos = location
        if location == -1:
            self.pos = hive.pos

        assert self.pos != None, "Bee agent {self} initialized with None position"

        self.state = state
        self.wiggle = wiggle
        self.wiggle_destiny = None # Location of bee resource once it finds it, which is passed to other bees if wiggle dancing 
        self.dancing_time = 0

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
            assert newpos != None, "New position for Bee agent {self} is equal to None"
            self.model.space.move_agent(self, newpos)
        else:
            # Retry so we ensure the bee moves and doesn't stay still
            # self.move_random_exploration()
            pass

    def is_close_to_hive(self):
        return self.is_close_to(self.hive, self.hive.radius)

    def is_close_to_resource(self, resource):
        return self.is_close_to(resource, resource.radius)
    
    def is_close_to(self, agent, threshold):
        return self.distance_to_agent(agent) <= threshold
    
    def move_towards_hive(self):
        self.move_towards(self.hive)

    def distance_to_agent(self, agent):
        if (self.pos == None or agent.pos == None):
            pass

        return np.hypot(self.pos[0] - agent.pos[0], self.pos[1] - agent.pos[1])

    def move_towards(self, destiny_agent):
        """
        Moves deterministically in straight line towards a target location
        """
        # TODO: Add stochasticity to dx and dy with weather :)
        dx = destiny_agent.pos[0] - self.pos[0]
        dy = destiny_agent.pos[1] - self.pos[1]
        
        distance = (dx**2 + dy**2)**0.5
        move_distance = Bee.SPEED * self.model.dt
        if distance > move_distance:
            angle = atan2(dy, dx)
            new_x = self.pos[0] + move_distance * cos(angle)
            new_y = self.pos[1] + move_distance * sin(angle)

            newpos = (new_x, new_y)
            assert newpos != None, "New position for Bee agent {self} is equal to None"

            self.model.space.move_agent(self, newpos)
        else:
            newpos = (destiny_agent.pos[0], destiny_agent.pos[1])
            assert newpos != None, "New position for Bee agent {self} is equal to None"

            self.model.space.move_agent(self, newpos)

    def step_by_caste(self):

        if self.state == Bee.State.RESTING: # Resting in the hive until changing mind and exploring
            assert self.load == 0, "Bee cannot be resting and carrying at the same time"
            assert self.wiggle == False, "Bee cannot be resting and wiggle dancing at the same time"
            assert self.wiggle_destiny == None, "Bee cannot be resting and have a wiggle destiny at the same time"
            assert self.is_close_to_hive(), "Bee cannot be resting and not close to hive"

            # Perceive resources locally
            if self.is_close_to_hive() and (self.hive.nectar < Bee.PERCEIVE_AS_LOW_FOOD):
                perceive_low_resources = True
            
            if perceive_low_resources:
                # Understand need for resource gathering
                self.state = Bee.State.EXPLORING
            return
        elif self.state == Bee.State.RETURNING: # Return straight to the hive and start resting
            if self.is_close_to_hive():
                self.state = Bee.State.RESTING
            else:
                self.move_towards_hive()
            return
        elif self.state == Bee.State.EXPLORING: # Exploring with random walk unless see waggle dances or choose to abort
            p_abort = Bee.P_ABORT_EXPLORING*self.model.dt
            if self.model.weather == Weather.STORM:
                p_abort *= Bee.STORM_ABORT_FACTOR

            if np.random.random() < p_abort:
                # Abort exploring and start returning to hive
                self.state = Bee.State.RETURNING
            else:
                # Try follow wiggle dance
                wiggling_bees_in_fov = np.array([other_agent for other_agent in self.model.agents if other_agent != self and isinstance(other_agent, Bee) and other_agent.wiggle and self.distance_to_agent(other_agent) <= self.fov])
                np.random.shuffle(wiggling_bees_in_fov)
                for wiggling_bee in wiggling_bees_in_fov:
                    if np.random.random() < Bee.P_FOLLOW_WIGGLE_DANCE:
                        self.wiggle_destiny = wiggling_bee.wiggle_destiny
                        self.state = Bee.State.FOLLOWING
                        return
                
                # Try gather resources
                resources_in_fov = [resource for resource in self.model.get_agents_of_type(Resource) if self.distance_to_agent(resource) <= self.fov]
                for resource in resources_in_fov:
                    if self.is_close_to_resource(resource):
                        self.wiggle_destiny = resource
                        self.state = Bee.State.CARRYING
                        return

                # Explore randomly
                self.move_random_exploration()
            return
        elif self.state == Bee.State.CARRYING: # Start carrying resources and bring back to the hive
            # Instantly gather resources
            if self.load == 0:
                self.load = Bee.CARRYING_CAPACITY

            # Fly back and deposit, then start dancing
            if self.is_close_to_hive():
                self.hive.nectar += self.load
                self.load = 0
                self.wiggle = True
                self.state = Bee.State.DANCING
            else:
                self.move_towards_hive()
            return
        elif self.state == Bee.State.DANCING: # Wiggle dance to communicate resource location
            self.dancing_time += self.model.dt
            # Rest if done dancing
            if self.dancing_time >= Bee.DANCING_TIME:
                self.dancing_time = 0
                self.wiggle_destiny = None
                self.wiggle = False
                self.state = Bee.State.RESTING
            return
        elif self.state == Bee.State.FOLLOWING: # Take straight path to waggle destiny resource if not aborting on the way
            # Carry resource if arrived
            if self.is_close_to_resource(self.wiggle_destiny):
                self.state = Bee.State.CARRYING
                # wiggle_destiny is already set to resource location
            
            # TODO: instead have it be scale based on distance to resource (i.e. expected time taken to get there)
            if np.random.random() < Bee.P_ABORT_FOLLOWING*self.model.dt:
                self.state = Bee.State.EXPLORING
            else:
                self.move_towards(self.wiggle_destiny)
            return
  
    def manage_death(self):
        self.fed -= Bee.STARVATION_SPEED*self.model.dt
        if self.fed <= 0: # Death by starvation
            # TODO: Mesa provides functionality to do that more efficiently
            self.model.n_agents_existed -= 1
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
            self.model.agents.remove(self)
            self.remove()
            # self.model.kill_agents.append(self)
            return
        
        self.age += self.model.dt
        if self.age >= Bee.MAX_AGE: # Death by age
            # TODO: Mesa provides functionality to do that more efficiently
            self.model.n_agents_existed -= 1
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
            self.model.agents.remove(self)
            self.remove()
            # self.model.kill_agents.append(self)
            return

        if self.model.weather == Weather.STORM and np.random.random() < Bee.P_DEATH_BY_STORM*self.model.dt: # Death by storm
            # TODO: Ensure bee is outside the hive
            # TODO: Mesa provides functionality to do that more efficiently
            self.model.n_agents_existed -= 1
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
            self.model.agents.remove(self)
            self.remove()
            # self.model.kill_agents.append(self)

            return