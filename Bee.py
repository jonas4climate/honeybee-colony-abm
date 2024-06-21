import random

from mesa import Agent
from Resource import Resource


class Bee(Agent):
    def __init__(self, model, location, hive, max_age=None):
        super().__init__(model.next_id(), model)
        self.location = location  # (x,y) -- FIXME mesa assumes `pos` attribute
        self.age = 0  # number of days
        self.max_age = max_age  # number of days (fixed)
        self.health = 1  # [0,1]
        self.interaction_range = 0  # distance at which the bee can interact with other agents
        self.carrying_food = False
        self.resting_duration = 5
        self.state = random.choice(["baby", "resting", "foraging", "dancing"])  # NOTE assumes equal probability of states
        #TODO initiate bees where they are assigned a mix of states

        # Hive information
        self.hive = hive  # Hive: the hive the bee belongs to
        self._hive_location = self.hive.location

    @property
    def in_hive(self):
        """Returns `True` if the bee is in the hive."""
        return self.location == self._hive_location

    def go_to_hive(self):
        self.move(self._hive_location)
        if self.in_hive():
            self.reach_hive()

    def reach_hive(self):
        if self.carrying_food:
            self.hive.store_food()
            self.carrying_food = False
        self.state = "resting"

    def move(self, target):
        # TODO : Random walk towards resource and pathfinder back to hive
        passs

    def step(self, dt=1):
        self.age += dt

    def manage_death(self):
        death = False
        if self.health <= 0: # Death by health
            death = True
        if self.max_age is not None and self.age >= self.max_age: # Death by age
            death = True
        if death:
            self.model.remove_agent(self)
            self.model.schedule.remove(self)

    def try_collect_resources(self):
        x, y = self.location
        neighbors = self.model.grid.get_neighbors(self.location, include_center=True, radius=self.interaction_range)
        resource_neighbors = [n for n in neighbors if isinstance(n, Resource)]
        # TODO : Make decision which resource to collect
        return
