"""
Model 1
Jonas, Bartek and Pablo
Based on the PDF Pablo sent on Saturday.
"""

from mesa import  Agent, Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation

import numpy as np
from typing import List

from .Bee import Bee, BeeState
from .Hive import Hive
from .Resource import Resource
from .Weather import Weather

class ForagerModel(Model):

    # Class properties
    storm_time_passed = 0       # Time duration of storm thus far
    size: int                   # side length of the square-shaped continuous space
    n_agents_existed: int       # counter for all the agents that were added to the model
    weather = Weather.NORMAL    # weather object
    
    space: ContinuousSpace      # continous space container from mesa package
    schedule: RandomActivation  # Scheduler from Mesa's time module
    agents: List[Agent]         # current list of agents

    p_storm: float              # probabilitiy of a storm occuring in a day
    storm_duration: float       # duration of the storm

    # Class constants
    P_STORM_DEFAULT = 1/10                    #1/(60*24*24*10)   # On average every 10 days (in seconds) | Probability of a storm
    STORM_DURATION_DEFAULT = 10               #60*60*24   # 1 day (in seconds) | Duration of a storm

    # Class methods
    def __init__(self, SIZE, n_hives, hive_locations, n_bees_per_hive, n_resources, resource_locations, dt=10_000,
                p_storm=P_STORM_DEFAULT, storm_duration=STORM_DURATION_DEFAULT):
        super().__init__()

        self.size = SIZE
        self.n_agents_existed = 0
        self.dt = dt                    # Time step in seconds

        self.space = ContinuousSpace(SIZE, SIZE, True)
        self.schedule = RandomActivation(self)
        self.agents = []

        # Weather parameters
        self.p_storm = p_storm
        self.storm_duration = storm_duration

        # Method to report weather events in scale with number of agents for easy plotting in same graph
        def get_weather(model):
            return model.n_agents_existed if model.weather == Weather.STORM else 0

        # TODO: Add foraging metrics from the literature, as defined in http://dx.doi.org/10.17221/7240-VETMED
        # TODO: Add method with % of each type of bee among all LIVING bees

        self.datacollector = DataCollector(
            model_reporters={'n_agents_existed': lambda mod: mod.n_agents_existed,
                             'weather_event': get_weather,
                             'prop_resting': lambda mod: mod.bees_proportion()["resting"],
                             'prop_returning': lambda mod: mod.bees_proportion()["returning"],
                             'prop_exploring': lambda mod: mod.bees_proportion()["exploring"],
                             'prop_carrying': lambda mod: mod.bees_proportion()["carrying"],
                             'prop_dancing': lambda mod: mod.bees_proportion()["dancing"],
                             'prop_following': lambda mod: mod.bees_proportion()["following"],
                             'nectar_in_hives': lambda mod: mod.nectar_in_hives(),

                             },             # Collect metrics from literature at every step
            agent_reporters={}              # As well as bee agent information
        )
        self.make_agents(n_hives, hive_locations, n_bees_per_hive, n_resources, resource_locations)

    def bees_proportion(self):
        all_bees = self.get_agents_of_type(Bee)
        if all_bees:
            return {state.value: len([a for a in all_bees if a.state == state]) / len(all_bees) for state in BeeState}
        else:
            return {state.value: 0 for state in BeeState}

    def nectar_in_hives(self):
        all_hives = self.get_agents_of_type(Hive)
        if all_hives:
            return sum([i.nectar for i in all_hives])

    def create_agent(self, agent_type, **kwargs):
        agent = agent_type(self.n_agents_existed, self, **kwargs)
        self.agents.append(agent)

        assert agent != None, f"Agent {agent} is None"
        assert agent.pos != None, f"Agent {agent} has None position"

        self.space.place_agent(agent, agent.pos)

        self.schedule.add(agent)
        self.n_agents_existed += 1

        return agent
    
    def create_agents(self, agent_type, n, **kwargs):
        agents = [self.create_agent(agent_type, **kwargs) for _ in range(n)]
        return agents
    
    def make_agents(self, n_hives, hive_locations, n_bees_per_hive, n_resources, resource_locations):
        assert len(hive_locations) == n_hives
        assert len(n_bees_per_hive) == n_hives
        assert len(resource_locations) == n_resources
        
        # Create Hives with their corresponding Bee agents
        for i in range(n_hives):
            current_hive = self.create_agent(Hive, location=hive_locations[i])
            for _ in range(n_bees_per_hive[i]):
                self.create_agent(Bee, hive=current_hive)
        
        # Create Resources
        for i in range(n_resources):
            self.create_agent(Resource, location=resource_locations[i])

    def step(self):
        self.schedule.step()
        self.manage_weather_events()
            
        # TODO: Add interaction of agents (?)
        self.datacollector.collect(self)    # Record step variables in the DataCollector

    def manage_weather_events(self):
        # Keep storming until storm duration passed
        if self.weather == Weather.STORM:
            self.storm_time_passed += self.dt
            if self.storm_time_passed >= self.storm_duration:
                self.weather = Weather.NORMAL
                self.storm_time_passed = 0

        # Start storming
        if np.random.random() < self.p_storm:
            self.weather = Weather.STORM