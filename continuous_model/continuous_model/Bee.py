from __future__ import annotations
from enum import Enum
from typing import Optional, Tuple

from mesa import Agent, Model
from math import atan2, cos, sin
import numpy as np
from scipy.stats import multivariate_normal, beta, expon

from .config import BeeSwarmConfig, HiveConfig
from .Resource import Resource
from .Weather import Weather


class BeeState(Enum):
    RESTING = "resting"
    RETURNING = "returning"
    EXPLORING = "exploring"
    CARRYING = "carrying"
    DANCING = "dancing"
    FOLLOWING = "following"


class BeeSwarm(Agent):
    def __init__(
        self,
        # id: int,  # unique identifier, required in mesa package
        model: Model,  # model the agent belongs to
        hive,  # the Hive the Bee agent belongs to
        fed: float = BeeSwarmConfig.FEED_STORAGE
    ):
        super().__init__(model.next_id() , model)
        self.hive = hive

        # Bees at birth are always located in the center of the hive and begin with resting state
        self.pos = hive.pos
        assert self.pos is not None, f"Bee agent {self} initialized with None position"
        self.state: BeeState = BeeState.RESTING

        self.wiggle = False
        self.wiggle_destiny: Optional[Tuple[float, float]] = None

        self.fed = fed
        self.load = 0.0  # agent amount of resources its carrying

        self.perceived_nectar = self.inspect_hive()

    def step(self):
        self.update_properties()  # Manage properties (age and fed)
        self.step_by_caste()  # Manage action based on caste
        self.manage_death()  # Manage death

    def scent_strength_at_pos(self, pos, resources, epsilon=1e-24):
        res_positions = [res.pos for res in resources]
        res_quantities = [res.quantity for res in resources]

        scent_intrigue = 0
        for res_pos, res_quant in zip(res_positions, res_quantities):
            res_distance = self.model.space.get_distance(pos, res_pos)
            dist_squared = res_distance**2 + epsilon # scent (diffusion) inversely proportional to distance squared (2D space)
            intensity = res_quant
            scent = intensity / dist_squared
            scent_intrigue += scent

        return scent_intrigue
    
    def inspect_hive(self, epsilon=1e-24):
        mu = self.hive.nectar / HiveConfig.MAX_NECTAR_CAPACITY
        if mu == 0:
            mu = epsilon
        a = BeeSwarmConfig.PERCEPTION * (mu)
        b = BeeSwarmConfig.PERCEPTION * (1 - mu)
        
        assert a > 0, f"Alpha parameter in Beta distribution is {a} but must be positive"
        assert b > 0, f"Beta parameter in Beta distribution is {b} but must be positive"

        if np.isclose(a, 0):
            a += np.finfo(np.float32).eps

        if np.isclose(b, 0):
            b += np.finfo(np.float32).eps

        self.perceived_nectar = beta.rvs(a, b)

        return self.perceived_nectar


    def move_random_exploration(self, epsilon=1e-12):
        """
        Moves randomly in x and y in the interval [-max_movement,max_movement]
        """
        distance = BeeSwarmConfig.SPEED * self.model.dt

        # Choose a random point with radius equivalent to speed times time step
        angle = np.random.uniform(0, 2 * np.pi)
        dx = distance * np.cos(angle)
        dy = distance * np.sin(angle)

        # Calculate the new position, taking the boundaries into account
        newx = self.pos[0] + dx
        newx = max(0, min(newx, self.model.size-epsilon))
        newy = self.pos[1] + dy
        newy = max(0, min(newy, self.model.size-epsilon))
        newpos = (newx, newy)

        # Calculate resource attraction bias
        resources = self.model.get_agents_of_type(Resource)
        if len(resources) == 0: # No resources left, just walk randomly
            self.model.space.move_agent(self, newpos)
        else: # Biased random walk
            attraction_current = self.scent_strength_at_pos(self.pos, resources)
            attraction_new = self.scent_strength_at_pos(newpos, resources)
            ratio = attraction_new / (attraction_current * (1 + BeeSwarmConfig.SCENT_SCALE))
    
            # Metropolis algorithm
            if attraction_new > attraction_current or np.random.random() < ratio:
                assert newpos != None, f"New position for Bee agent {self} is equal to None"
                self.model.space.move_agent(self, newpos)
            else:
                # If we walk here, we guarantee speed to be consistent but loose property of Metropolis walk
                pass

    @property
    def is_outside(self):
        return not self.is_close_to_hive()
    
    def is_resource_in_sight(self, resource):
        return self.is_close_to(resource, resource.radius + BeeSwarmConfig.FIELD_OF_VIEW)

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
            return np.inf
            # raise ValueError(f"Position of agent {self} or {agent} is None")
        return self.model.space.get_distance(self.pos, agent.pos)

    def move_towards(self, destiny_agent):
        """
        Moves deterministically in straight line towards a target location
        """
        if destiny_agent.pos == None:
            # NOTE: not smooth, if we don't know where we are going because the agent disappeared (e.g. resource used up), we just go back to exploring
            self.wiggle_destiny = None
            self.state = BeeState.EXPLORING
            return
        # TODO: Add stochasticity to dx and dy with weather :)
        dx = destiny_agent.pos[0] - self.pos[0]
        dy = destiny_agent.pos[1] - self.pos[1]

        distance = (dx**2 + dy**2) ** 0.5
        move_distance = BeeSwarmConfig.SPEED * self.model.dt
        if distance > move_distance:
            angle = atan2(dy, dx)
            new_x = self.pos[0] + move_distance * cos(angle)
            new_y = self.pos[1] + move_distance * sin(angle)

            newpos = (new_x, new_y)
            assert newpos != None, f"New position for Bee agent {self} is equal to None"

            self.model.space.move_agent(self, newpos)
        else:
            newpos = (destiny_agent.pos[0], destiny_agent.pos[1])
            assert newpos != None, f"New position for Bee agent {self} is equal to None"

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
        # assert (self.wiggle_destiny is None), (f"Bee cannot be resting and have a wiggle destiny at the same time (currently: {self.wiggle_destiny}, self.state: {self.state}). Location: {self.pos}, Hive_location: {self.hive.pos}.")
        assert self.is_close_to_hive(), "Bee cannot be resting and not close to hive"

        if np.random.random() < BeeSwarmConfig.P_NECTAR_INSPECTION*self.model.dt:
            # Inspect hive resources with fixed probability
            self.inspect_hive()
        elif np.random.random() < BeeSwarmConfig.P_NECTAR_COMMUNICATION*self.model.dt:
            # If not inspecting, communicate the information with random nearby bee
            nearby_bees = self.model.space.get_neighbors(self.pos, BeeSwarmConfig.FIELD_OF_VIEW)
            nearby_bees = [bee for bee in nearby_bees if isinstance(bee, BeeSwarm) and bee != self]

            if len(nearby_bees) > 0:
                # Pick a random neighboring bee and share the nectar perception
                random_neighbor = nearby_bees[np.random.randint(0, len(nearby_bees))]       # np.random.choice() is the way to go but can be slow
                random_neighbor.perceived_nectar = self.perceived_nectar

        # Start exploring based on exponential distribution
        # TODO: Normalize nectar capacity and perceived nectar to one unit
        if np.random.random() < expon.pdf(self.perceived_nectar * HiveConfig.MAX_NECTAR_CAPACITY / 1000, scale=BeeSwarmConfig.EXPLORING_INCENTIVE):
            # print(expon.pdf(self.perceived_nectar * HiveConfig.MAX_NECTAR_CAPACITY / 1000, scale=BeeConfig.EXPLORING_INCENTIVE))

            self.state = BeeState.EXPLORING

    def handle_returning(self):
        if self.is_close_to_hive():
            self.state = BeeState.RESTING
        else:
            self.move_towards_hive()

    def handle_exploring(self):
        p_abort = BeeSwarmConfig.P_ABORT_EXPLORING * self.model.dt
        if self.model.weather == Weather.STORM:
            p_abort *= BeeSwarmConfig.STORM_ABORT_FACTOR
        if np.random.random() < p_abort:
            self.state = BeeState.RETURNING
        else:
            self.try_follow_wiggle_dance()
            self.try_gather_resources()
            self.move_random_exploration()

    def handle_carrying(self):
        # Instantly gather resources
        # TODO: If we don't vary the load, this variable can be deleted
        if self.load == 0:
            self.load = BeeSwarmConfig.CARRYING_CAPACITY

        # Fly back and deposit, then start dancing
        if self.is_close_to_hive():
            self.hive.nectar = min(self.hive.nectar + self.load, HiveConfig.MAX_NECTAR_CAPACITY)
            self.load = 0
            self.wiggle = True
            self.state = BeeState.DANCING
        else:
            self.move_towards_hive()

    def handle_dancing(self):
        self.wiggle_destiny = None
        self.wiggle = False
        self.state = BeeState.RESTING

    def handle_following(self):
        # Check safely if close to resource (could have disappeared), carry resource if arrived
        if self.wiggle_destiny and self.is_close_to_resource(self.wiggle_destiny):
            self.state = BeeState.CARRYING
            # wiggle_destiny is already set to resource location

        # TODO: instead have it be scale based on distance to resource (i.e. expected time taken to get there)
        p_abort_following = BeeSwarmConfig.P_ABORT_FOLLOWING * self.model.dt
        if self.model.weather == Weather.STORM:
            p_abort_following *= BeeSwarmConfig.STORM_ABORT_FACTOR
        if np.random.random() < p_abort_following:
            self.state = BeeState.EXPLORING
        else:
            self.move_towards(self.wiggle_destiny)

    def try_follow_wiggle_dance(self):
        agents_in_fov = self.model.space.get_neighbors(
            self.pos, BeeSwarmConfig.FIELD_OF_VIEW, include_center=True
        )
        wiggling_bees_in_fov = np.array(
            [
                agent
                for agent in agents_in_fov
                if agent != self
                and isinstance(agent, BeeSwarm)
                and agent.wiggle
            ]
        )
        np.random.shuffle(wiggling_bees_in_fov)
        for wiggling_bee in wiggling_bees_in_fov:
            if np.random.random() < BeeSwarmConfig.P_FOLLOW_WIGGLE_DANCE:
                self.wiggle_destiny = wiggling_bee.wiggle_destiny
                self.state = BeeState.FOLLOWING
                return

    def try_gather_resources(self):
        resources = self.model.get_agents_of_type(Resource)

        for res in resources:
            if self.is_close_to_resource(res):
                self.wiggle_destiny = res
                self.state = BeeState.CARRYING
                self.extract(res)
                return
            
    def extract(self, resource: Resource):
        max_load_capacity = BeeSwarmConfig.CARRYING_CAPACITY
        if resource.persistent == True:
            self.load = max_load_capacity
        else:
            extract_amount = min(resource.quantity, max_load_capacity)
            self.load = extract_amount
            resource.quantity -= extract_amount
            # print(f'Resource quantity: {resource.quantity} | {self} gathered {extract_amount}')

    def update_properties(self):
        """Updates the properties of the bee."""
        self.fed = max(
            self.fed - BeeSwarmConfig.STARVATION_SPEED * self.model.dt, 0
        )  # ensure fed is not negative

    def manage_death(self):
        """Handles tiny bee deaths."""
        if self.fed == 0:  # Death by starvation
            print("Bee died by starvation")
            return self._remove_agent()

        if (
            self.model.weather == Weather.STORM
            and np.random.random() < BeeSwarmConfig.P_DEATH_BY_STORM * self.model.dt
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
