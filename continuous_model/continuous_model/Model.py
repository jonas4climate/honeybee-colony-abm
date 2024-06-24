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

from .Bee import Bee
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
    def __init__(self, SIZE, n_hives, hive_locations, n_bees_per_hive, n_resources, resource_locations, dt=1,
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
        self.datacollector = DataCollector(
            model_reporters={'n_agents_existed': lambda mod: mod.n_agents_existed,
                             'weather_event': get_weather},             # Collect metrics from literature at every step
            agent_reporters={}              # As well as bee agent information
        )

        self.make_agents(n_hives, hive_locations, n_bees_per_hive, n_resources, resource_locations)

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
        # TODO: self.schedule.step()

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