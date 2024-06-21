import random

from mesa import Agent

from Resource import Resource
from States import STATES_STEP

class Bee(Agent):
    def __init__(self, model, location, hive, max_age=None):
        super().__init__(model.next_id(), model)
        self.location = location  # (x,y) -- FIXME mesa assumes `pos` attribute
        self.age = 0  # number of days
        self.max_age = max_age  # number of days (fixed)

        # State variables
        self.state = random.choice(["baby", "resting", "foraging", "dancing"])  # FIXME : Assumes equal probability of states
        self.state_step = STATES_STEP[self.state]  # function to execute for the assigned bee state
        self.energy = 1  # percentage of energy left in the bee
        # self.energy_consumption = 0.1  # percentage of food depleted by bees per day
        self.resting_duration = 5  # FIXME : Hardcoded
        self.interaction_range = 0  # distance at which the bee can interact with other agents
        #TODO initiate bees where they are assigned a mix of states
        
        # Foraging information
        self.current_capacity = 1  # 1 = free, 0 = carrying resource
        self.current_trajectory = []  # list of locations to visit 
        self.carrying_resource = False  # True if the bee is carrying a resource
        # self.food_capacity = 1  # TODO : Implement

        # Hive information
        self.hive = hive  # Hive: the hive the bee belongs to
        self._hive_location = self.hive.location

    @property
    def in_hive(self):
        """Return `True` if the bee is in the hive."""
        return self.location == self._hive_location
    
    @property
    def has_resource(self):
        """Return `True` if the bee is carrying food."""
        return self.carrying_resource

    def kill(self):
        self.model.remove_agent(self)

    def go_to_hive(self):
        """Move the bee to the hive and store the food if it is carrying some."""
        self.move(self._hive_location)
        if self.in_hive():
            self.reach_hive()

    def reach_hive(self):
        if self.carrying_food:
            self.hive.store_food()
            self.carrying_food = False
        self.state = "resting"

    def step(self, dt=1):
        """Advance the bee by one time step."""
        self.age += dt
        self.energy -= 0.5 # FIXME : Hardcoded
        if ( self.energy <= 0 ) or ( self.max_age is not None and self.age >= self.max_age ):
            self.kill()
        else:
            self.state_step(self)

    # def try_collect_resources(self):
    #     x, y = self.location
    #     neighbors = self.model.grid.get_neighbors(self.location, include_center=True, radius=self.interaction_range)
    #     resource_neighbors = [n for n in neighbors if isinstance(n, Resource)]
    #     # TODO : Make decision which resource to collect
    #     return
    
    def move(self, target):
        """Move the bee to the target location."""
        self.model.grid.move_agent(self, target)

    def random_walk(self):
        """Move the bee to a random neighboring cell."""
        neighbors = self.model.grid.get_neighborhood(self.location, moore=True, include_center=False)
        new_location = self.random.choice(neighbors)
        self.move(new_location)
