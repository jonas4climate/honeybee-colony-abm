"""
Model 1
Jonas, Bartek and Pablo
Based on the PDF Pablo sent on Saturday.
"""

from enum import Enum
from random import shuffle
from .CustomScheduler import CustomScheduler
from .Weather import Weather
from .Resource import Resource
from .Hive import Hive
from .config import *
from .Bee import BeeSwarm, BeeState
from .Analytics import *
from typing import List, Tuple
import numpy as np
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace
from mesa import Agent, Model
import warnings
warnings.simplefilter(action='ignore', category=UserWarning)


class ForagerModel(Model):
    def __init__(
        self,
        model_config: ModelConfig,
        hive_config: HiveConfig,
        beeswarm_config: BeeSwarmConfig,
        resource_config: ResourceConfig,
        distance_from_hive = None,
        **kwargs
    ):
        super().__init__()

        self.size = model_config.size  # side length of the square-shaped continuous space
        self.n_agents_existed = 0  # counter for all the agents that were added to the model
        self.dt = model_config.dt  # Time step in seconds

        self.hive_config = hive_config  # Pass on when creating Hive agents
        self.beeswarm_config = beeswarm_config  # Pass on when creating Bee agents
        self.resource_config = resource_config

        # continous space container from mesa package
        self.space = ContinuousSpace(self.size, self.size, False)
        # Scheduler from Mesa's time module
        self.schedule = CustomScheduler(self)

        # Weather parameters
        self.weather = Weather.NORMAL  # weather object
        # probabilitiy of a storm occuring in a day
        self.p_storm = model_config.p_storm_default
        self.storm_duration = model_config.storm_duration_default  # duration of the storm
        self.storm_time_passed = 0  # Time duration of storm thus far

        # Override config with visualization input options if passed on
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.setup_datacollector(model_config.n_hives)
        hive_locations, resource_locations = self.init_space(
            self.size, self.size, model_config.n_resource_sites, model_config.n_hives, model_config.space_setup, distance_from_hive)
        self.init_agents_in_space(
            hive_locations, model_config.n_beeswarms, resource_locations)
        
        self.wiggle_dancing_bees = set() # Keep track of all bees currently wiggle dancing

    def inspect_setup(self):
        visualize_scent_scale(get_scent_scale(self))

    def setup_datacollector(self, n_hives):
        # TODO: Add foraging metrics from the literature, as defined in http://dx.doi.org/10.17221/7240-VETMED
        # TODO: Add method with % of each type of bee among all LIVING bees
        def get_weather(model):
            return get_bee_count(model.schedule) if model.weather == Weather.STORM else 0

        model_reporters = {
            'n_agents_existed': lambda mod: mod.n_agents_existed,
            'Bee count 🐝': lambda mod: get_bee_count(mod.schedule),
            'Storm ⛈️': get_weather,
            'resting 💤': lambda mod: bees_proportion(mod)["resting"],
            'returning 🔙': lambda mod: bees_proportion(mod)["returning"],
            'exploring 🗺️': lambda mod: bees_proportion(mod)["exploring"],
            'carrying 🎒': lambda mod: bees_proportion(mod)["carrying"],
            'dancing 🪩': lambda mod: bees_proportion(mod)["dancing"],
            'following 🎯': lambda mod: bees_proportion(mod)["following"],
            'Average feed level of bees 🐝': lambda mod: average_bee_fed(mod),
            'Mean perceived nectar level': lambda mod: mean_perceived_nectar(mod),
        }

        # Dynamically add nectar in hives
        for i in range(n_hives):
            model_reporters[f'Hive ({
                i+1}) stock 🍯'] = lambda mod: nectar_in_hives(mod)[i]

        agent_reporters = {}

        self.datacollector = DataCollector(
            model_reporters=model_reporters,
            agent_reporters=agent_reporters
        )

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

    def init_agents_in_space(self, hive_locations, n_bees_per_hive, resource_locations):

        for i in range(len(hive_locations)):
            current_hive = self.create_agent(Hive, location=hive_locations[i])
            for _ in range(n_bees_per_hive):
                self.create_agent(BeeSwarm, hive=current_hive)

        for i in range(len(resource_locations)):
            self.create_agent(Resource, location=resource_locations[i])

    def step(self):
        self.schedule.step()
        self.manage_weather_events()

        # TODO: Add interaction of agents (?)
        # Record step variables in the DataCollector
        self.datacollector.collect(self)

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
    def init_space(width, height, n_resources, n_hives, space_setup, distance_from_hive):
        """Initialize the space with resources and hives."""
        if space_setup == SpaceSetup.RANDOM:
            positions = [(x, y) for x in range(0, width, 10)
                         for y in range(0, height, 10)]
            shuffle(positions)
            resource_locations = positions[0:n_resources]
            if n_hives != 1:
                i_hives = n_resources + n_hives
                hive_locations = positions[n_resources:i_hives]
            else:
                # for 1 hive, place at center
                hive_locations = [[width/2, height/2]]
            return hive_locations, resource_locations
        elif space_setup == SpaceSetup.FIXED_DISTANCE_FROM_HIVE:
            hive_locations = [[width/2, height/2]]
            assert distance_from_hive != None, "Distance from hive must be specified in this mode."
            resource_locations = [(width/2 + distance_from_hive, height/2)]
            return hive_locations, resource_locations
