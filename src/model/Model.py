import numpy as np
from random import shuffle
from enum import Enum

from .agents.BeeSwarm import BeeSwarm
from .agents.Resource import Resource
from .agents.Hive import Hive

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace
from mesa.time import BaseScheduler

from .config.ModelConfig import ModelConfig
from .config.BeeSwarmConfig import BeeSwarmConfig
from .config.HiveConfig import HiveConfig
from .config.ResourceConfig import ResourceConfig
from .config.VisualConfig import VisualConfig as VC

from .util.Weather import Weather
from .util.Analytics import *
from .util.ModelBuilder import *

class RunMode(Enum):
    EXPERIMENTS = 0
    SERVER = 1
    SENSITIVITY_ANALYSIS = 2

class ForagerModel(Model):
    def __init__(self, model_config=ModelConfig(), bee_config=BeeSwarmConfig(), hive_config=HiveConfig(), resource_config=ResourceConfig(),
                 run_mode=RunMode.EXPERIMENTS, p_storm=None, storm_duration=None, n_resources=None, resource_dist=None):
        super().__init__()

        if run_mode == RunMode.EXPERIMENTS:
            assert n_resources == None, "This parameter is reserved for JS server visualization. Use ModelBuilder class to create resources."
            assert resource_dist == None, "This parameter is reserved for JS server visualization. Use ModelBuilder class to create resources."
            assert p_storm == None, "This parameter is reserved for JS server visualization. Use ModelConfig instance to change weather parameters."
            assert storm_duration == None, "This parameter is reserved for JS server visualization. Use ModelConfig instance to change weather parameters."
        elif run_mode == RunMode.SERVER:
            assert n_resources != None, "You are running the model in JS server visualization mode. Provide number of resources as direct parameter."
            assert resource_dist != None, "You are running the model in JS server visualization mode. Provide distance to resources as direct parameter."
            assert p_storm != None, "You are running the model in JS server visualization mode. Provide probability of storm as direct parameter."
            assert storm_duration != None, "You are running the model in JS server visualization mode. Provide storm duration as direct parameter."
        elif run_mode == RunMode.SENSITIVITY_ANALYSIS:
            assert n_resources != None, "You are running the model in sensitivity analysis mode. Provide number of resources as direct parameter."
            assert resource_dist != None, "You are running the model in sensitivity analysis mode. Provide distance to resources as direct parameter."

        # Side length of the square-shaped continuous space
        self.size = ModelConfig.SIZE

        # Continous space container from mesa package
        self.space = ContinuousSpace(self.size, self.size, False)
        
        # Scheduler from Mesa's time module
        self.schedule = BaseScheduler(self)

        # Configuration of parameters related to bee agents
        self.bee_config = bee_config

        # Configuration of parameters related to hive agent
        self.hive_config = hive_config

        # Configuration of parameters related to resource agents
        self.resource_config = resource_config

        # Weather state
        self.weather = Weather.SUNNY

        # Probability of a storm event occuring
        if run_mode == RunMode.SERVER:
            self.p_storm = p_storm
        else:
            self.p_storm = model_config.P_STORM

        # Storm event duration
        if run_mode == RunMode.SERVER:
            self.storm_duration = storm_duration
        elif run_mode == RunMode.CLASSIC:
            self.storm_duration = model_config.STORM_DURATION

        # Time duration of storm event thus far
        self.storm_time_passed = 0

        # Set up the data collector
        self.setup_datacollector()

        # One single hive in the center of the space
        self.hive = self.create_agent(Hive, (self.size // 2, self.size // 2))

        # Create bee agents
        for _ in range(hive_config.N_BEES):
            self.create_agent(BeeSwarm, self.hive.pos, hive=self.hive)

        # If running JS server visualization or sensitivity analysis, automatically spawn resources, otherwise use ModelBuilder class.
        if run_mode == RunMode.SERVER or run_mode == RunMode.SENSITIVITY_ANALYSIS:
            for _ in range(n_resources):
                add_resource_in_distance(self, resource_dist, quantity=resource_config.QUANTITY)

    @property
    def is_sunny(self):
        return self.weather == Weather.SUNNY

    @property
    def is_raining(self):
        return self.weather == Weather.RAIN
    
    @staticmethod
    def is_bee(agent):
        return isinstance(agent, BeeSwarm)

    @staticmethod
    def is_hive(agent):
        return isinstance(agent, Hive)
    
    @staticmethod
    def is_resource(agent):
        return isinstance(agent, Resource)

    def setup_datacollector(self):

        def get_weather(model):
            return get_bee_count(model) if model.weather == Weather.RAIN else 0

        model_reporters = {
            'Bee count 🐝': lambda mod: get_bee_count(mod),
            'Storm ⛈️': get_weather,
            'resting 💤': lambda mod: bees_proportion(mod)["resting"],
            'returning 🔙': lambda mod: bees_proportion(mod)["returning"],
            'exploring 🗺️': lambda mod: bees_proportion(mod)["exploring"],
            'carrying 🎒': lambda mod: bees_proportion(mod)["carrying"],
            'dancing 🪩': lambda mod: bees_proportion(mod)["dancing"],
            'following 🎯': lambda mod: bees_proportion(mod)["following"],
            'Mean perceived nectar level': lambda mod: mean_perceived_nectar(mod),
            'Hive stock 🍯': lambda mod: self.hive.nectar
        }

        agent_reporters = {}

        self.datacollector = DataCollector(
            model_reporters=model_reporters,
            agent_reporters=agent_reporters
        )

    def plot(self, ax):
        ax.set_xlim(self.space.x_min, self.space.x_max)
        ax.set_ylim(self.space.y_min, self.space.y_max)
        ax.set_aspect('equal', 'box')

        hive_circle = plt.Circle(self.hive.pos, HC.RADIUS, color=VC.HIVE_COLOR)
        ax.add_patch(hive_circle)
        
        for bee in self.get_agents_of_type(BeeSwarm):
            bee_circle = plt.Circle(bee.pos, 1, color=VC.BEE_COLORS[bee.state])
            ax.add_patch(bee_circle)
        
        for resource in self.get_agents_of_type(Resource):
            resource_circle = plt.Circle(resource.pos, RC.RADIUS, color=VC.RESOURCE_COLOR(resource))
            ax.add_patch(resource_circle)

    def create_agent(self, agent_type, location, **kwargs):
        agent = agent_type(self, **kwargs)

        assert agent != None, f"Agent {agent} is None"
        assert agent.pos == None, f"Agent {agent} should have None position"

        self.space.place_agent(agent, location)
        self.schedule.add(agent)

        return agent

    def step(self):
        self.schedule.step()
        self.manage_weather_events()

        # Record step variables in the DataCollector
        self.datacollector.collect(self)

    def manage_weather_events(self):
        """
        Manages the weather. Turns rain on and off.
        """
        # Keep raining until storm duration passed
        if self.is_raining:
            self.storm_time_passed += 1
            if self.storm_time_passed >= self.storm_duration:
                self.weather = Weather.SUNNY
                self.storm_time_passed = 0

        # Start raining
        if np.random.random() < self.p_storm:
            self.weather = Weather.RAIN