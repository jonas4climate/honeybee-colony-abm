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
from typing import List, Tuple

from .Bee import BeeSwarm, BeeState
from .config import ModelConfig
from .Hive import Hive
from .Resource import Resource
from .Weather import Weather
from .CustomScheduler import CustomScheduler
from random import shuffle

class ForagerModel(Model):
    def __init__(
        self, 
        size: int, 
        n_hives: int = ModelConfig.N_HIVES,
        # hive_locations: List[Tuple[int, int]],
        # n_resources: int,
        # resource_locations: List[Tuple[int, int]],
        n_resources: int = ModelConfig.N_RESOURCE_SITES,
        n_bees_per_hive: int = ModelConfig.N_BEESWARMS,
        dt: int = ModelConfig.DT,
        p_storm: float = ModelConfig.P_STORM_DEFAULT, 
        storm_duration: float = ModelConfig.STORM_DURATION_DEFAULT
    ):
        super().__init__()

        self.size = size  # side length of the square-shaped continuous space
        self.n_agents_existed = 0  # counter for all the agents that were added to the model
        self.dt = dt  # Time step in seconds

        self.space = ContinuousSpace(size, size, False)  # continous space container from mesa package
        self.schedule = CustomScheduler(self)  # Scheduler from Mesa's time module

        # Weather parameters
        self.weather = Weather.NORMAL  # weather object
        self.p_storm = p_storm  # probabilitiy of a storm occuring in a day
        self.storm_duration = storm_duration  # duration of the storm
        self.storm_time_passed = 0  # Time duration of storm thus far

        self.setup_datacollector()
        hive_locations, resource_locations = self.init_space(size, size, n_resources, n_hives)
        self.make_agents(hive_locations, n_bees_per_hive, resource_locations)

    def setup_datacollector(self):
        # TODO: Add foraging metrics from the literature, as defined in http://dx.doi.org/10.17221/7240-VETMED
        # TODO: Add method with % of each type of bee among all LIVING bees
        def get_weather(model):
            return model.schedule.get_bee_count() if model.weather == Weather.STORM else 0

        model_reporters = {
            'n_agents_existed': lambda mod: mod.n_agents_existed,
            'Bee count 🐝': lambda mod: mod.schedule.get_bee_count(),
            'Storm ⛈️': get_weather,
            'resting 💤': lambda mod: mod.bees_proportion()["resting"],
            'returning 🔙': lambda mod: mod.bees_proportion()["returning"],
            'exploring 🗺️': lambda mod: mod.bees_proportion()["exploring"],
            'carrying 🎒': lambda mod: mod.bees_proportion()["carrying"],
            'dancing 🪩': lambda mod: mod.bees_proportion()["dancing"],
            'following 🎯': lambda mod: mod.bees_proportion()["following"],
            'Mean perceived nectar level': lambda mod: mod.mean_perceived_nectar(),
        }

        # Dynamically add nectar in hives
        for i in range(ModelConfig.N_HIVES):
            model_reporters[f'Hive ({i+1}) stock 🍯'] = lambda mod: mod.nectar_in_hives()[i]

        agent_reporters = {}

        self.datacollector = DataCollector(
            model_reporters=model_reporters,
            agent_reporters=agent_reporters
        )

    def bees_proportion(self):
        all_bees = self.get_agents_of_type(BeeSwarm)
        if all_bees:
            return {state.value: len([a for a in all_bees if a.state == state]) / len(all_bees) for state in BeeState}
        else:
            return {state.value: 0 for state in BeeState}

    def nectar_in_hives(self):
        all_hives = self.get_agents_of_type(Hive)
        if all_hives:
            return [i.nectar for i in all_hives]
        else:
            raise Exception("No hives in the model")
    
    def mean_perceived_nectar(self):
        all_bees = self.get_agents_of_type(BeeSwarm)
        if all_bees:
            return np.mean([b.perceived_nectar for b in all_bees])
        else:
            return 0

    def create_agent(self, agent_type, **kwargs):
        # TODO: fix, we are getting warnings about an agent being placed twice / having a position already
        agent = agent_type(self, **kwargs)
        # self.agents.append(agent)

        assert agent != None, f"Agent {agent} is None"
        assert agent.pos != None, f"Agent {agent} has None position"

        self.space.place_agent(agent, agent.pos)

        self.schedule.add(agent)
        self.n_agents_existed += 1

        return agent
    
    def create_agents(self, agent_type, n, **kwargs):
        agents = [self.create_agent(agent_type, **kwargs) for _ in range(n)]
        return agents
    
    def make_agents(self, hive_locations, n_bees_per_hive, resource_locations):
        # assert len(hive_locations) == n_hives
        # assert len(resource_locations) == n_resources
        
        # Create Hives with their corresponding Bee agents
        for i in range(len(hive_locations)):
            current_hive = self.create_agent(Hive, location=hive_locations[i])
            for _ in range(n_bees_per_hive):
                self.create_agent(BeeSwarm, hive=current_hive)
        
        # Create Resources
        for i in range(len(resource_locations)):
            self.create_agent(Resource, location=resource_locations[i])

    def step(self):
        self.schedule.step()
        self.manage_weather_events()
            
        # TODO: Add interaction of agents (?)
        self.datacollector.collect(self)    # Record step variables in the DataCollector

    def kill_agent(self, agent):
        self.schedule.remove(agent)
        self.space.remove_agent(agent)
        self.n_agents_existed -= 1

    def manage_weather_events(self):
        # Keep storming until storm duration passed
        if self.weather == Weather.STORM:
            self.storm_time_passed += self.dt
            if self.storm_time_passed >= self.storm_duration:
                self.weather = Weather.NORMAL
                self.storm_time_passed = 0

        # Start storming
        if np.random.random() < self.p_storm*self.dt:
            self.weather = Weather.STORM

    @staticmethod
    def init_space(width, height, n_resources, n_hives):
        """Initialize the space with resources and hives."""
        positions = [(x, y) for x in range(0, width, 10) for y in range(0, height, 10)]

        shuffle(positions)

        resource_location = positions[0:n_resources]
        if n_hives != 1:
            i_hives = n_resources + n_hives
            hive_location = positions[n_resources:i_hives]
        else:
            # for 1 hive, place at center
            hive_location = [[width/2, height/2]]
        return hive_location, resource_location

