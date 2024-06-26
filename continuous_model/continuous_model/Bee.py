from __future__ import annotations
from enum import Enum
from typing import Optional, Tuple

from mesa import Agent, Model
from math import atan2, cos, sin, sqrt
import numpy as np
from scipy.stats import multivariate_normal

from .config import BeeConfig
# from .Hive import Hive
from .Resource import Resource
from .Weather import Weather


class BeeState(Enum):
    RESTING = "resting"
    RETURNING = "returning"
    EXPLORING = "exploring"
    CARRYING = "carrying"
    DANCING = "dancing"
    FOLLOWING = "following"


class Bee(Agent):
    def __init__(
        self,
        id: int,  # unique identifier, required in mesa package
        model: "Model",  # model the agent belongs to
        hive,  # the Hive the Bee agent belongs to
        location: Optional[Tuple[float, float]] = None, # agent's current position
        fov: float = BeeConfig.FIELD_OF_VIEW,  # radius around the agent in which it can perceive the environment
        age: float = 0,  # agent's current age (which has influence on their activity)
        fed: float = 1.0,
        state: BeeState = BeeState.RESTING,  # Bee's current activity
        wiggle: bool = False,  # whether the Bee agent is currently wiggle dancing
    ):
        super().__init__(id, model)
        self.hive = hive
        self.pos = location if location is not None else hive.pos
        assert self.pos is not None, f"Bee agent {self} initialized with None position"

        self.state = state
        self.wiggle = wiggle
        self.wiggle_destiny: Optional[Tuple[float, float]] = None
        self.dancing_time = 0

        self.age = age
        self.fov = fov
        self.fed = fed
        self.load = 0.0  # agent amount of resources its carrying

    def step(self):
        self.update_properties()  # Manage properties (age and fed)
        self.step_by_caste()  # Manage action based on caste
        self.manage_death()  # Manage death

    def resource_attraction(self, pos):
        attraction = 0.0

        resource_positions = np.array(
            [resource.pos for resource in self.model.get_agents_of_type(Resource)]
        )
        pos_array = np.array(pos)  # ensure typing (not sure if necessary tho)
        cov_matrix = self.model.size  # TODO: calibrate better
        pdf_values = multivariate_normal.pdf(
            resource_positions, mean=pos_array, cov=cov_matrix
        )
        attraction = np.sum(pdf_values)

        # for resource in self.model.get_agents_of_type(Resource):
        #    attraction += multivariate_normal.pdf(list(pos), list(resource.pos), cov=self.model.size)

        return attraction

    def move_random_exploration(self):
        """
        Moves randomly in x and y in the interval [-max_movement,max_movement]
        """
        distance = BeeConfig.SPEED * self.model.dt
        # Choose a random point with radius equivalent to speed times time step
        angle = np.random.uniform(0, 2 * np.pi)
        dx = distance * np.cos(angle)
        dy = distance * np.sin(angle)

        # Calculate the new position, taking the boundaries into account
        newx = self.pos[0] + dx
        newx = max(-newx, min(self.model.size, newx))

        newy = self.pos[1] + dy
        newy = max(-newy, min(self.model.size, newy))

        newpos = (newx, newy)

        # Calculate resource attraction bias
        # TODO: Use bee STATE to incorporate different biases in random walk!
        # TODO: Positive bias towards the resources
        attraction_current = self.resource_attraction(self.pos)
        attraction_new = self.resource_attraction(newpos)

        # TODO: Negative bias away from the hive
        # dist_to_hive = np.hypot(newpos[0] - self.hive.pos[0], newpos[1] - self.hive.pos[1])
        # if dist_to_hive < BeeConfig.HIVE_MOVE_AWAY_TH:

        # Metropolis algorithm
        if attraction_new > attraction_current or np.random.random() < (
            attraction_new / attraction_current
        ):
            assert newpos != None, "New position for Bee agent {self} is equal to None"
            self.model.space.move_agent(self, newpos)
        else:
            # Retry so we ensure the bee moves and doesn't stay still
            # self.move_random_exploration()
            pass

    @property
    def is_outside(self):
        return not self.is_close_to_hive()

    def is_close_to_hive(self):
        return self.is_close_to(self.hive, self.hive.radius)

    def is_close_to_resource(self, resource):
        return self.is_close_to(resource, resource.radius)

    def is_close_to(self, agent, threshold):
        return self.distance_to_agent(agent) <= threshold

    def move_towards_hive(self):
        self.move_towards(self.hive)

    def distance_to_agent(self, agent):
        if self.pos == None or agent.pos == None:
            pass

        return np.hypot(self.pos[0] - agent.pos[0], self.pos[1] - agent.pos[1])

    def move_towards(self, destiny_agent):
        """
        Moves deterministically in straight line towards a target location
        """
        # TODO: Add stochasticity to dx and dy with weather :)
        dx = destiny_agent.pos[0] - self.pos[0]
        dy = destiny_agent.pos[1] - self.pos[1]

        distance = (dx**2 + dy**2) ** 0.5
        move_distance = BeeConfig.SPEED * self.model.dt
        if distance > move_distance:
            angle = atan2(dy, dx)
            new_x = self.pos[0] + move_distance * cos(angle)
            new_y = self.pos[1] + move_distance * sin(angle)

            newpos = (new_x, new_y)
            assert newpos != None, "New position for Bee agent {self} is equal to None"

            self.model.space.move_agent(self, newpos)
        else:
            newpos = (destiny_agent.pos[0], destiny_agent.pos[1])
            assert newpos != None, "New position for Bee agent {self} is equal to None"

            self.model.space.move_agent(self, newpos)

    def step_by_caste(self):
        """Handles the bee's actions based on caste."""
        if self.state == BeeState.RESTING:
            return self.handle_resting()
        elif self.state == BeeState.RETURNING:
            return self.handle_returning()
        elif self.state == BeeState.EXPLORING:
            return self.handle_exploring()
        elif self.state == BeeState.CARRYING:
            return self.handle_carrying()
        elif self.state == BeeState.DANCING:
            return self.handle_dancing()
        elif self.state == BeeState.FOLLOWING:
            return self.handle_following()

    def handle_resting(self):
        assert self.load == 0, "Bee cannot be resting and carrying at the same time"
        assert (
            not self.wiggle
        ), "Bee cannot be resting and wiggle dancing at the same time"
        assert (
            self.wiggle_destiny is None
        ), "Bee cannot be resting and have a wiggle destiny at the same time"
        assert self.is_close_to_hive(), "Bee cannot be resting and not close to hive"

        # Perceive resources locally, if low start exploring
        if self.is_close_to_hive() and (self.hive.nectar < BeeConfig.PERCEIVE_AS_LOW_FOOD):
            self.state = BeeState.EXPLORING

    def handle_returning(self):
        if self.is_close_to_hive():
            self.state = BeeState.RESTING
        else:
            self.move_towards_hive()

    def handle_exploring(self):
        p_abort = BeeConfig.P_ABORT_EXPLORING * self.model.dt
        if self.model.weather == Weather.STORM:
            p_abort *= BeeConfig.STORM_ABORT_FACTOR
        if np.random.random() < p_abort:
            self.state = BeeState.RETURNING
        else:
            self.try_follow_wiggle_dance()
            self.try_gather_resources() if self.state == BeeState.EXPLORING else None
            (
                self.move_random_exploration()
                if self.state == BeeState.EXPLORING
                else None
            )

    def handle_carrying(self):
        # Instantly gather resources
        if self.load == 0:
            self.load = BeeConfig.CARRYING_CAPACITY

        # Fly back and deposit, then start dancing
        if self.is_close_to_hive():
            self.hive.nectar += self.load
            self.load = 0
            self.wiggle = True
            self.state = BeeState.DANCING
        else:
            self.move_towards_hive()

    def handle_dancing(self):
        self.dancing_time += self.model.dt
        # Rest if done dancing
        if self.dancing_time >= BeeConfig.DANCING_TIME:
            self.dancing_time = 0
            self.wiggle_destiny = None
            self.wiggle = False
            self.state = BeeState.RESTING

    def handle_following(self):
        # Carry resource if arrived
        if self.is_close_to_resource(self.wiggle_destiny):
            self.state = BeeState.CARRYING
            # wiggle_destiny is already set to resource location

        # TODO: instead have it be scale based on distance to resource (i.e. expected time taken to get there)
        if np.random.random() < BeeConfig.P_ABORT_FOLLOWING * self.model.dt:
            self.state = BeeState.EXPLORING
        else:
            self.move_towards(self.wiggle_destiny)

    def try_follow_wiggle_dance(self):
        wiggling_bees_in_fov = np.array(
            [
                other_agent
                for other_agent in self.model.agents
                if other_agent != self
                and isinstance(other_agent, Bee)
                and other_agent.wiggle
                and self.distance_to_agent(other_agent) <= self.fov
            ]
        )
        np.random.shuffle(wiggling_bees_in_fov)
        for wiggling_bee in wiggling_bees_in_fov:
            if np.random.random() < BeeConfig.P_FOLLOW_WIGGLE_DANCE:
                self.wiggle_destiny = wiggling_bee.wiggle_destiny
                self.state = BeeState.FOLLOWING
                return

    def try_gather_resources(self):
        resources_in_fov = [
            resource
            for resource in self.model.get_agents_of_type(Resource)
            if self.distance_to_agent(resource) <= self.fov
        ]
        for resource in resources_in_fov:
            if self.is_close_to_resource(resource):
                self.wiggle_destiny = resource
                self.state = BeeState.CARRYING
                return

    def update_properties(self):
        """Updates the properties of the bee."""
        self.fed = max(
            self.fed - BeeConfig.STARVATION_SPEED * self.model.dt, 0
        )  # ensure fed is not negative
        self.age += self.model.dt

    def manage_death(self):
        """Handles tiny bee deaths."""
        if self.fed == 0:  # Death by starvation
            print("Bee died by starvation")
            return self._remove_agent()

        if self.age >= BeeConfig.MAX_AGE:  # Death by age
            print("Bee died by age")
            return self._remove_agent()

        if (
            self.model.weather == Weather.STORM
            and np.random.random() < BeeConfig.P_DEATH_BY_STORM * self.model.dt
        ):  # Death by storm
            if self.is_outside:
                print("Bee died by storm")
                return self._remove_agent()

    def _remove_agent(self):
        """Helper for removing agents."""
        # TODO: Mesa provides functionality to do that more efficiently
        self.model.n_agents_existed -= 1
        self.model.space.remove_agent(self)
        self.model.schedule.remove(self)
        self.model.agents.remove(self)
        self.remove()
