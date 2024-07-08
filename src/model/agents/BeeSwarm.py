from __future__ import annotations

from typing import Optional, Tuple

from mesa import Agent, Model
from math import atan2, cos, sin
import numpy as np
from numpy.random import random
from scipy.stats import expon, uniform

from .Resource import Resource
from ..util.BeeState import BeeState

from ..config.BeeSwarmConfig import BeeSwarmConfig as BSC
from ..config.HiveConfig import HiveConfig as HC

class BeeSwarm(Agent):

    def __init__(
        self,
        model: Model,  # model the agent belongs to
        hive,  # the Hive the Bee agent belongs to
    ):
        super().__init__(model.next_id() , model)

        # The hive the bee agent belongs to
        self.hive = hive

        # Agent's position in space
        self.pos = None

        # Agent's current activity
        self.state: BeeState = BeeState.RESTING

        # Destination of resource communicated through waggle dance recruitment
        self.resource_destination: Optional[Tuple[float, float]] = None

        # Time spent resting after successful foraging trip
        self.resting_time = 0

        # Agent's perceived amount of resources available in the hive
        self.perceived_nectar = 0.0

        # Inspect hive and change perceived nectar value
        self.inspect_hive()

    @property
    def is_resting(self):
        return self.state == BeeState.RESTING

    @property
    def is_returning(self):
        return self.state == BeeState.RETURNING

    @property
    def is_exploring(self):
        return self.state == BeeState.EXPLORING

    @property
    def is_carrying(self):
        return self.state == BeeState.CARRYING

    @property
    def is_dancing(self):
        return self.state == BeeState.DANCING

    @property
    def is_following(self):
        return self.state == BeeState.FOLLOWING

    def step(self):
        """Agent's step function required by Mesa package."""
        self.step_by_activity()         # Manage action based on current activity
        self.manage_death()             # Manage death

    def scent_strength_at_pos(self, pos, resources, epsilon=1e-24):
        """Calculates scent (attraction) of all Resource agents at the specific position in space.

        Args:
            pos (Tuple[float, float]): position at which attraction is calculated
            resources (List[Resource]): list of resources to calculate the scent for
            epsilon (float, optional): small number to handle edge cases. Defaults to 1e-24.

        Returns:
            float: scent strength at the given position
        """

        # Obtain positions and quantities of Resource agents
        res_positions = [res.pos for res in resources]
        res_quantities = [res.quantity for res in resources]

        scent_intrigue = 0

        # Iterate over all resources
        for res_pos, res_quant in zip(res_positions, res_quantities):
            
            # Squared distance to the resource
            res_distance = self.model.space.get_distance(pos, res_pos)
            dist_squared = res_distance**2 + epsilon

            # Scent is dependent on resource quantity and squared distance to that resource
            scent = res_quant / dist_squared
            scent_intrigue += scent

        return scent_intrigue
    
    def inspect_hive(self):
        """
        Bee agent inspects the hive and samples perceived nectar level from Beta distribution.
        """
        # Mean of the Beta distribution, equal to normalized nectar level within hive
        self.perceived_nectar = max(self.hive.nectar + uniform.rvs(-1, 1), 0)

    def move_random_in_hive(self):
        """
        Moves randomly in x and y in the interval [-distance, distance]
        """
        # Choose a random point with radius equivalent to speed times time step
        angle = np.random.uniform(0, 2 * np.pi)
        dx = self.model.bee_config.SPEED_IN_HIVE * np.cos(angle)
        dy = self.model.bee_config.SPEED_IN_HIVE * np.sin(angle)

        # Calculate the new position, taking the boundaries into account
        newx = self.pos[0] + dx
        newy = self.pos[1] + dy
        newpos = (newx, newy)
        
        # Repeat untill the new position is within the hive
        while self.model.space.get_distance(self.hive.pos, newpos) > HC.RADIUS:
            angle = np.random.uniform(0, 2 * np.pi)
            dx = self.model.bee_config.SPEED_IN_HIVE * np.cos(angle)
            dy = self.model.bee_config.SPEED_IN_HIVE * np.sin(angle)

            # Calculate the new position, taking the boundaries into account
            newx = self.pos[0] + dx
            newy = self.pos[1] + dy
            newpos = (newx, newy)

        self.model.space.move_agent(self, newpos)

    def move_random_exploration(self, epsilon=1e-12):
        """
        Moves randomly in x and y in the interval [-max_movement,max_movement]
        """
        # Distance the bee agent will cover in the simulation step
        # TODO: Add stochasticity to the distance covered.

        # Choose a random point with radius equivalent to speed times time step
        angle = np.random.uniform(0, 2 * np.pi)
        dx = self.model.bee_config.SPEED_FORAGING * np.cos(angle)
        dy = self.model.bee_config.SPEED_FORAGING * np.sin(angle)

        # Calculate the new position, taking the boundaries into account
        newx = self.pos[0] + dx
        newx = max(0, min(newx, self.model.size-epsilon))
        newy = self.pos[1] + dy
        newy = max(0, min(newy, self.model.size-epsilon))
        newpos = (newx, newy)

        # Calculate resource attraction bias
        resources = self.model.get_agents_of_type(Resource)

        # Attraction level at current and new position
        attraction_current = self.scent_strength_at_pos(self.pos, resources)
        attraction_new = self.scent_strength_at_pos(newpos, resources)

        # If all resources depleted, just move
        if attraction_current == 0:
            self.model.space.move_agent(self, newpos)
        else:
            ratio = attraction_new / (attraction_current * 10)

            # Metropolis algorithm
            if attraction_new > attraction_current or random() < ratio:
                self.model.space.move_agent(self, newpos)

    @property
    def is_in_hive(self):
        """
        Check if the bee agent is within hive area. Syntactic sugar.
        """
        return self.is_close_to(self.hive, HC.RADIUS)
    
    def is_close_to(self, agent, threshold):
        """Determines if bee agent is in close proximity to another agent.

        Args:
            agent (Agent): agent to determine proximity for
            threshold (float): proximity threshold

        Returns:
            bool: True if the bee agent is in close proximity to the other agent
        """
        return self.model.space.get_distance(self.pos, agent.pos) <= threshold

    def is_close_to_resource(self, resource):
        """
        Determines if bee agent is in close proximity to specific resource. Syntactic sugar.
        """
        return self.is_close_to(resource, resource.radius)

    def move_towards_hive(self):
        """
        Moves the bee agent towards their hive. Syntactic sugar.
        """
        self.move_towards(self.hive)

    def move_towards(self, destination):
        """
        Moves deterministically in straight line towards a target location.
        """
        # TODO: Add stochasticity to the distance covered

        # Determines distance to the destination
        distance = self.model.space.get_distance(self.pos, destination.pos)

        # Move towards the destination.
        if distance > self.model.bee_config.SPEED_FORAGING:
            dx = destination.pos[0] - self.pos[0]
            dy = destination.pos[1] - self.pos[1]

            angle = atan2(dy, dx)
            new_x = self.pos[0] + self.model.bee_config.SPEED_FORAGING * cos(angle)
            new_y = self.pos[1] + self.model.bee_config.SPEED_FORAGING * sin(angle)

            newpos = (new_x, new_y)
            assert newpos != None, f"New position for Bee agent {self} is equal to None"

            self.model.space.move_agent(self, newpos)
        else:
            newpos = (destination.pos[0], destination.pos[1])
            assert newpos != None, f"New position for Bee agent {self} is equal to None"

            self.model.space.move_agent(self, newpos)

    def step_by_activity(self):
        """Handles the bee's actions based on their current activity."""
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
        """
        Handles the behaviour of a bee resting in the hive.
        """
        self.move_random_in_hive()

        if random() < self.model.bee_config.P_NECTAR_INSPECTION:
            # Inspect hive resources with fixed probability
            self.inspect_hive()
        elif random() < self.model.bee_config.P_NECTAR_COMMUNICATION:
            # If not inspecting, communicate the information with all nearby bees
            nearby_bees = self.model.space.get_neighbors(self.pos, self.model.bee_config.FOV, include_center=False)

            for bee in nearby_bees:
                if isinstance(bee, BeeSwarm) and random() < self.model.bee_config.P_NECTAR_COMMUNICATION:
                    bee.perceived_nectar = self.perceived_nectar

        # Start exploring based on exponential distribution and self-perceived nectar
        if self.resting_time == 0 and random() < expon.pdf(self.perceived_nectar, scale=self.model.bee_config.EXPLORING_INCENTIVE):
            self.state = BeeState.EXPLORING
        else:
            self.resting_time = max(self.resting_time - 1, 0)

    def handle_returning(self):
        """
        Handles the behaviour of a bee returning to the hive without carrying resources.
        """
        if self.is_in_hive:
            self.state = BeeState.RESTING
            self.resting_time = self.model.bee_config.RESTING_PERIOD
        else:
            self.move_towards_hive()

    def handle_exploring(self):
        """
        Handles the behaviour of bee exploring the space for resources.
        """
        # Abort exploration with certain probability, otherwise continue moving towards the resource
        if self.model.is_raining or random() < self.model.bee_config.P_ABORT:
            self.state = BeeState.RETURNING
        else:
            self.move_random_exploration()

    def handle_carrying(self):
        """
        Handles the behaviour of bee carrying the resource back to the hive.
        """
        # TODO: Waggle dance should be performed with probability dependent on resource profitability
        # Fly back and put the resources in the hive, then start waggle dancing
        if self.is_in_hive:
            self.hive.nectar += self.model.bee_config.CARRYING_CAPACITY
            self.state = BeeState.DANCING
        else:
            self.move_towards_hive()

    def handle_dancing(self):
        """
        Handles the behaviour of a waggle dancing bee.
        """
        assert self.resource_destination != None

        # Find nearby resting bees and try to employ them with certain probability
        nearby_resting_bees = self.model.space.get_neighbors(self.pos, self.model.bee_config.FOV, include_center=False)
        nearby_resting_bees = list(filter(lambda bee : isinstance(bee, BeeSwarm) and bee.state == BeeState.RESTING, nearby_resting_bees))

        for bee in nearby_resting_bees:
            if bee.resting_time == 0 and random() < self.model.bee_config.P_FOLLOW_WAGGLE_DANCE:
                bee.state = BeeState.FOLLOWING
                bee.resource_destination = self.resource_destination

        self.state = BeeState.RESTING
        self.resting_time = self.model.bee_config.RESTING_PERIOD
        self.resource_destination = None

    def handle_following(self):
        """
        Handles the behaviour of a bee recruited through waggle dance.
        """
        # Abort recruitment with certain probability, otherwise continue moving towards the resource
        if self.model.is_raining or random() < self.model.bee_config.P_ABORT:
            self.state = BeeState.RETURNING
        else:
            assert self.resource_destination != None
            self.move_towards(self.resource_destination)

    def manage_death(self):
        """Handles death of BeeSwarm agent."""
        death_factor = self.model.bee_config.P_DEATH

        # Higher death chance during storm
        if self.model.is_raining:
            death_factor *= self.model.bee_config.DEATH_STORM_FACTOR
    
        if not self.is_in_hive and random() < self.model.bee_config.P_DEATH:
            # Death by random outside risk
            return self._remove_agent()
        elif self.is_in_hive and random() < 0.1 * expon.pdf(self.hive.nectar, scale=1):
            # Death by hunger
            return self._remove_agent()

    def _remove_agent(self):
        """Helper for removing agents."""
        self.model.space.remove_agent(self)
        self.model.schedule.remove(self)
        self.model.agents.remove(self)
        self.remove()
