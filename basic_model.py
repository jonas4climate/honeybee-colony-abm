"""
Starting model definition, consisting on bees, hives and resources
"""

import mesa
from mesa import Agent, Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
from enum import Enum

class Bee(Agent):
    def __init__(self, id, model, age, health, caste, location, BeeHive, max_age=None):
        super().__init__(id, model)
        self.age = age                              # Float: number of days
        self.max_age = max_age                      # Float: number of days (fixed)
        self.health = health                        # Float: [0,1]
        self.caste = caste                          # String: "worker", "forager", "etc..."
        self.location = location                    # Tuple: (x,y)
        self.hive = BeeHive                         # Hive: the hive the bee belongs to
        self.interaction_range = 0                  # Float: distance at which the bee can interact with other agents
        # TODO: Complete

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
        if self.caste == Caste.FORAGER:
            # If not carrying resource, go follow scout information somehow to find resources
            self.try_collect_resources()
            # If carrying resource, go bring it back to the hive, trace back steps?
            pass
        elif self.caste == Caste.SCOUT:
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

    def is_in_hive(self):
        x, y = self.location
        return True if x**2 + y**2 < self.hive.radius else False
    
    def try_collect_resources(self):
        x, y = self.location
        neighbors = self.model.space.get_neighbors(self.location, moore=True, include_center=True, radius=self.interaction_range)
        resource_neighbors = [n for n in neighbors if isinstance(n, Resource)]
        # Make decision which resource to collect
        return

class Caste(Enum):
    FORAGER = "forager"
    SCOUT = "scout"

class BeeHive(Agent):
    def __init__(self, id, model, location, radius):
        super().__init__(id, model)
        self.location = location                    # (x,y) tuple
        self.radius = radius                        # Beehive has a circle shape, size may change with population
        # TODO: Complete    

    def step(self):
        pass

class Resource(Agent):
    def __init__(self, id, model, location, type, quantity, persistent):
        super().__init__(id, model)
        self.location = location                    # (x,y) tuple
        self.type = type                            # "honey", "water",...
        self.quantity = quantity                    # Float: [0,1]
        self.persistent = persistent                # Bool: True if resource lasts forever
        # TODO: Complete

    def step(self):
        # Should replentish or go extinct if quantity reaches 0
        pass    

# TODO: Define model, including step
class BeeModel(Model):

    def __init__(self, SIZE):
        super().__init__()
        self.size = SIZE                                        # Int: Size of the square space considered for the simulation
        self.space = ContinuousSpace(SIZE, SIZE, True)
        self.n_agents_existed = 0                               # Counter for all agents to have created, used as unique id
        self.agents = []                                        # List of all agents in the model

        # TODO: Add foraging metrics from the literature, as defined in http://dx.doi.org/10.17221/7240-VETMED
        self.datacollector = DataCollector(
            model_reporters={},             # Collect metrics from literature at every step
            agent_reporters={}              # As well as bee agent information
        )

    def create_agent(self, agent_type, **kwargs):
        agent = agent_type(self.n_agents_existed, self, **kwargs)
        self.agents.append(agent)
        self.space.place_agent(agent, agent.location)
        self.n_agents_existed += 1
        return agent
    
    def create_agents(self, agent_type, n, **kwargs):
        agents = [self.create_agent(agent_type, **kwargs) for _ in range(n)]
        return agents

    def step(self):
        for agent in self.agents:
            agent.step()
        # TODO: Add interaction of agents (?)
        self.datacollector.collect(self)    # Record step variables in the DataCollector
        # TODO: self.schedule.step()