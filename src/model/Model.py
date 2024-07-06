import numpy as np
from random import shuffle

from .agents.BeeSwarm import BeeSwarm
from .agents.Resource import Resource
from .agents.Hive import Hive

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace
from mesa.time import BaseScheduler

from .config.ModelConfig import ModelConfig as MC
from .config.BeeSwarmConfig import BeeSwarmConfig as BSC
from .config.HiveConfig import HiveConfig as HC
from .config.ResourceConfig import ResourceConfig as RC
from .config.VisualConfig import VisualConfig as VC
from .config.VisualConfig import VisualMode

from .util.Weather import Weather
from .util.Analytics import *
from .util.ModelBuilder import *

class ForagerModel(Model):
    def __init__(self, p_storm=MC.P_STORM_DEFAULT, storm_duration=MC.STORM_DURATION_DEFAULT,
                viz_mode=VisualMode.CLASSIC, n_resources=None, resource_dist=None):
        super().__init__()

        if viz_mode == VisualMode.CLASSIC:
            assert n_resources == None, "This parameter is reserved for JS server visualization. Use ModelBuilder class to run your simulations."
            assert resource_dist == None, "This parameter is reserved for JS server visualization. Use ModelBuilder class to run your simulations."
        elif viz_mode == VisualMode.SERVER:
            assert n_resources != None, "VisualMode.SERVER is reserved for JS server visualization. To run your simulations use VisualMode.CLASSIC"
            assert resource_dist != None, "VisualMode.SERVER is reserved for JS server visualization. To run your simulations use VisualMode.CLASSIC"

        # Side length of the square-shaped continuous space
        self.size = MC.SIZE

        # Continous space container from mesa package
        self.space = ContinuousSpace(self.size, self.size, False)
        
        # Scheduler from Mesa's time module
        self.schedule = BaseScheduler(self)

        # Weather state
        self.weather = Weather.SUNNY

        # Probability of a storm event occuring
        self.p_storm = p_storm

        # Storm event duration
        self.storm_duration = storm_duration

        # Time duration of storm event thus far
        self.storm_time_passed = 0

        # Set up the data collector
        self.setup_datacollector()

        # One single hive in the center of the space
        self.hive = self.create_agent(Hive, (self.size // 2, self.size // 2))

        # Create bee agents
        for _ in range(HC.N_BEES):
            self.create_agent(BeeSwarm, self.hive.pos, hive=self.hive)

        # If running JS server visualization, spawn resources, otherwise use ModelBuilder class.
        if viz_mode == VisualMode.SERVER:
            for _ in range(n_resources):
                add_resource_in_distance(self, resource_dist, quantity=RC.DEFAULT_QUANTITY)

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