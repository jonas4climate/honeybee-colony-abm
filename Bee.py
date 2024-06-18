from mesa import Agent
from Resource import Resource
from enum import Enum
from BeeHive import BeeHive
import random



class Bee(Agent):
    class State(Enum):
        RESTING = "resting"  # in the hive, resting & not interested in foraging
        DANCEFLOOR = "dancefloor"  # in the hive, on the dancefloor
        READY = "ready"  # in the hive, ready to forage
        RECRUITING = "recruiting"  # in the hive, recruiting other bees to forage
        FULL_RETURN = "full_return"  # returned from foraging with resources (success)
        EMPTY_RETURN = "empty_return"  # returned from foraging without resources (no success)
        SCOUTING = "scouting"  # scouting for resources as a result of spontaneous "decision"
        FORAGING = "foraging"  # foraging for resources as a result of recruitment
        BORN = "baby"  # in the hive, just born


    def __init__(self, model, location, BeeHive, max_age=None):
        super().__init__(id, model)
        self.age = 0                              # Float: number of days
        self.max_age = max_age                      # Float: number of days (fixed)
        self.health = 1                             # Float: [0,1]
        self.caste = Bee.State.BORN                     # String: "worker", "forager", "etc..."
        self.location = location                    # Tuple: (x,y)
        self.interaction_range = 0                  # Float: distance at which the bee can interact with other agents
        self.carrying_food = False

        # Hive information
        self.hive = BeeHive  # Hive: the hive the bee belongs to
        self._hive_location = self.hive.location



    def in_hive(self):
        return self.location == self._hive_location

    def go_to_hive(self):
        self.move(self._hive_location)

        if self.in_hive():
            self.reach_hive()

    def reach_hive(self):
        if self.carrying_food:
            self.hive.store_food()
            self.carrying_food = False

        self.state = Bee.State.RESTING

    def move(self, new_location):
        # TODO: Implement an algorithm for random movement in the beginning and pathfinder when going back to hive


    def step(self, dt=1):
        # Manage action based on caste
        self.step_by_caste(dt)

        # Manage ageing
        self.age += dt

        # Manage caste change
        self.manage_caste_change()
        
        # Manage death
        self.manage_death()

    def step_by_caste(self, dt):
        if self.caste == Bee.State.FORAGING:
            # If not carrying resource, go follow scout information somehow to find resources
            self.try_collect_resources()
            # If carrying resource, go bring it back to the hive, trace back steps?
            pass
        elif self.caste == Bee.State.SCOUTING:
            # Go perform some kind of optimization search for resources / random search / etc...
            # Communicate information somehow
            pass
        else:
            raise ValueError("Caste not recognized")

    def manage_caste_change(self):
        pass

    # TODO: Add method to make forager put back resource in hive

    def manage_death(self):
        death = False
        if self.health <= 0: # Death by health
            death = True
        if self.max_age is not None and self.age >= self.max_age: # Death by age
            death = True

        if death:
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
        return

    def try_collect_resources(self):
        x, y = self.location
        neighbors = self.model.space.get_neighbors(self.location, include_center=True, radius=self.interaction_range)
        resource_neighbors = [n for n in neighbors if isinstance(n, Resource)]
        # Make decision which resource to collect
        return

