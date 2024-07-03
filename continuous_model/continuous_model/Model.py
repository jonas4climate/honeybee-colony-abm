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

from .Analytics import *
from .Bee import BeeSwarm
from .config import *
from .Hive import Hive
from .Resource import Resource
from .Weather import Weather
from .CustomScheduler import CustomScheduler
from random import shuffle

class ForagerModel(Model):
    def __init__(
        self,
        model_config: ModelConfig,
        hive_config: HiveConfig,
        beeswarm_config: BeeSwarmConfig,
        resource_config: ResourceConfig,
        **kwargs
    ):
        super().__init__()

        self.size = model_config.size  # side length of the square-shaped continuous space
        self.n_agents_existed = 0  # counter for all the agents that were added to the model
        self.dt = model_config.dt  # Time step in seconds

        self.hive_config = hive_config # Pass on when creating Hive agents
        self.beeswarm_config = beeswarm_config # Pass on when creating Bee agents
        self.resource_config = resource_config

        self.space = ContinuousSpace(self.size, self.size, False)  # continous space container from mesa package
        self.schedule = CustomScheduler(self)  # Scheduler from Mesa's time module

        # Weather parameters
        self.weather = Weather.NORMAL  # weather object
        self.p_storm = model_config.p_storm_default  # probabilitiy of a storm occuring in a day
        self.storm_duration = model_config.storm_duration_default  # duration of the storm
        self.storm_time_passed = 0  # Time duration of storm thus far
        self.n_beeswarms_initial = model_config.n_beeswarms

        # Override config with visualization input options if passed on
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.setup_datacollector(model_config.n_hives)
        hive_locations, resource_locations = self.init_space(self.size, self.size, model_config.n_resource_sites, model_config.n_hives)
        self.make_agents(hive_locations, self.n_beeswarms_initial, resource_locations)

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
            model_reporters[f'Hive ({i+1}) stock 🍯'] = lambda mod: nectar_in_hives(mod)[i]

        agent_reporters = {}

        self.datacollector = DataCollector(
            model_reporters=model_reporters,
            agent_reporters=agent_reporters
        )

    def create_agent(self, agent_type, location, **kwargs):
        # TODO: fix, we are getting warnings about an agent being placed twice / having a position already
        agent = agent_type(self, **kwargs)
        # self.agents.append(agent)
        
        assert agent != None, f"Agent {agent} is None"
        self.space.place_agent(agent, location)

        assert agent.pos != None, f"Agent {agent} has None position"

        self.schedule.add(agent)
        self.n_agents_existed += 1

        return agent
    
    def make_agents(self, hive_locations, n_bees_per_hive, resource_locations):
        # assert len(hive_locations) == n_hives
        # assert len(resource_locations) == n_resources
        
        # Create Hives with their corresponding Bee agents
        for i in range(len(hive_locations)):
            current_hive = self.create_agent(Hive, location=hive_locations[i])
            for _ in range(n_bees_per_hive):
                self.create_agent(BeeSwarm, location=hive_locations[i], hive=current_hive)
        
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

    def plot(self, ax):
        ax.set_xlim(self.space.x_min, self.space.x_max)
        ax.set_ylim(self.space.y_min, self.space.y_max)
        ax.set_aspect('equal', 'box')

        for hive in self.get_agents_of_type(Hive):
            hive_circle = plt.Circle(hive.pos, hive.radius, color=VisualConfig.hive_color)
            ax.add_patch(hive_circle)
        
        for bee in self.get_agents_of_type(BeeSwarm):
            bee_circle = plt.Circle(bee.pos, 2, color=VisualConfig.bee_colors[bee.state])
            ax.add_patch(bee_circle)
        
        for resource in self.get_agents_of_type(Resource):
            resource_circle = plt.Circle(resource.pos, resource.radius, color=VisualConfig.resource_color)
            ax.add_patch(resource_circle)

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

