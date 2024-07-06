from __future__ import annotations
from enum import Enum
from typing import Optional, Tuple

from mesa import Agent, Model
from math import atan2, cos, sin
import numpy as np
from numpy.random import random
from scipy.stats import expon, uniform

from .Resource import Resource
from ..util.Weather import Weather

class BeeState(Enum):
    RESTING = "resting"
    RETURNING = "returning"
    READY = "ready"
    EXPLORING = "exploring"
    CARRYING = "carrying"
    DANCING = "dancing"
    FOLLOWING = "following"

class BeeSwarm(Agent):
    # Quantity deducted from in-hive bee's hunger level at each step
    FOOD_CONSUMPTION = 0.01
    # Amount of distance covered by the BeeSwarm agent in a single step
    SPEED = 1
    # How eager the bee is to explore based on current resources
    EXPLORING_INCENTIVE = 30
    # Field of view of a bee in which it is capable of interacting with other bees
    FOV = 1
    # Probability for each bee in the hive to asses nectar resources at the given simulation step
    P_NECTAR_INSPECTION = 0.1
    # Probability for each bee in the hive to communicate their perceived nectar level to other bee
    P_NECTAR_COMMUNICATION = 0.1
    # Amount of resource the Bee agent can carry
    CARRYING_CAPACITY = 0.01
    # Maximal time spent in the ready state, awaiting for recruitment or starting exploration
    MAX_READY_TIME = 20

    def __init__(
        self,
        model: Model,  # model the agent belongs to
        hive,  # the Hive the Bee agent belongs to
    ):
        super().__init__(model.next_id() , model)

        # The hive the bee agent belongs to
        self.hive = hive

        # Agent's position in space
        self.pos = hive.pos

        # Agent's current activity
        self.state: BeeState = BeeState.RESTING

        # Destination of resource communicated through waggle dance recruitment
        self.resource_destination: Optional[Tuple[float, float]] = None

        # Amount of time spent in the ready state [s]
        self.ready_time: int = 0

        # Agent's perceived amount of resources available in the hive
        self.perceived_nectar = 0.0

        # Inspect hive
        self.inspect_hive()

    @property
    def is_resting(self):
        return self.state == BeeState.RESTING

    @property
    def is_returning(self):
        return self.state == BeeState.RETURNING

    @property
    def is_ready(self):
        return self.state == BeeState.READY

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
        dx = self.speed_in_hive * np.cos(angle)
        dy = self.speed_in_hive * np.sin(angle)

        # Calculate the new position, taking the boundaries into account
        newx = self.pos[0] + dx
        newy = self.pos[1] + dy
        newpos = (newx, newy)
        
        # Repeat untill the new position is within the hive
        while self.model.space.get_distance(self.hive.pos, newpos) > self.hive.radius:
            angle = np.random.uniform(0, 2 * np.pi)
            dx = self.speed_in_hive * np.cos(angle)
            dy = self.speed_in_hive * np.sin(angle)

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
        distance = self.speed * self.model.dt

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
        else:
            # Attraction level at current and new position
            attraction_current = self.scent_strength_at_pos(self.pos, resources)
            attraction_new = self.scent_strength_at_pos(newpos, resources)

            assert attraction_current > 0, f"Current attraction is {attraction_current} but must be > 0"
            assert 1 + self.scent_scale > 0, f"Scent scale is {self.scent_scale} but must be > 0"
            ratio = attraction_new / (attraction_current * (1 + self.scent_scale))
    
            # Metropolis algorithm
            if attraction_new > attraction_current or random() < ratio:
                assert newpos != None, f"New position for Bee agent {self} is equal to None"
                self.model.space.move_agent(self, newpos)
            else:
                pass
    @property
    def is_in_hive(self):
        """
        Check if the bee agent is within hive area. Syntactic sugar.
        """
        return self.is_close_to(self.hive, self.hive.radius)
    
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
        if distance > BeeSwarm.SPEED:
            dx = destination.pos[0] - self.pos[0]
            dy = destination.pos[1] - self.pos[1]

            angle = atan2(dy, dx)
            new_x = self.pos[0] + self.SPEED * cos(angle)
            new_y = self.pos[1] + self * sin(angle)

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
        elif self.state == BeeState.READY:
            return self.handle_ready()
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

        if random() < self.P_NECTAR_INSPECTION:
            # Inspect hive resources with fixed probability
            self.inspect_hive()
        elif random() < self.P_NECTAR_COMMUNICATION:
            # If not inspecting, communicate the information with all nearby bees
            nearby_bees = self.model.space.get_neighbors(self.pos, BeeSwarm.FOV, include_center=False)

            for bee in nearby_bees:
                if isinstance(bee, BeeSwarm) and random() < self.p_nectar_communcation:
                    bee.perceived_nectar = self.perceived_nectar
        
        # Start exploring based on exponential distribution
        if random() < expon.sf(self.perceived_nectar, scale=BeeSwarm.EXPLORING_INCENTIVE):
            self.state = BeeState.READY

    def handle_returning(self):
        """
        Handles the behaviour of a bee returning to the hive without carrying resources.
        """
        if self.is_in_hive:
            self.state = BeeState.RESTING
        else:
            self.move_towards_hive()

    def handle_ready(self):
        """
        Handles the behaviour of a bee ready to explore or become recruited.
        """
        self.move_random_in_hive()

        # Increment time spent in a ready state
        self.ready_time += 1
        
        # If bored with being ready decide to explore or go back to resting
        if  (self.ready_time > BeeSwarm.MAX_READY_TIME):
            self.ready_time = 0

            # Start exploring based on exponential distribution (other bees could have communicated change in perceived nectar level)
            if  random() < expon.sf(self.perceived_nectar, scale=BeeSwarm.EXPLORING_INCENTIVE):
                self.state = BeeState.EXPLORING
            else:
                self.state = BeeState.RESTING

    def handle_exploring(self):
        """
        Handles the behaviour of bee exploring the space for resources.
        """
        # Abort exploration with certain probability, otherwise continue moving towards the resource
        if self.model.is_raining or random() < self.p_abort:
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
            self.hive.nectar += BeeSwarm.CARRYING_CAPACITY
            self.state = BeeState.DANCING
        else:
            self.move_towards_hive()

    def handle_dancing(self):
        """
        Handles the behaviour of a waggle dancing bee.
        """
        # Find nearby ready bees and try to employ them with certain probability
        nearby_ready_bees = self.model.space.get_neighbors(self.pos, BeeSwarm.FOV, include_center=False)
        nearby_ready_bees = list(filter(lambda bee : isinstance(bee, BeeSwarm) and bee.state == BeeState.READY, nearby_ready_bees))

        for bee in nearby_ready_bees:
            if random() < self.p_follow_waggle_dance:
                bee.resource_destination = self.resource_destination
                bee.state = BeeState.FOLLOWING

        self.state = BeeState.RESTING
        self.resource_destination = None

    def handle_following(self):
        """
        Handles the behaviour of a bee recruited through waggle dance.
        """
        # Check safely if close to resource (could have disappeared), carry resource if arrived
        if self.resource_destination and self.is_close_to_resource(self.resource_destination):
            self.state = BeeState.CARRYING

        # Abort recruitment with certain probability, otherwise continue moving towards the resource
        if self.model.weather == Weather.STORM or random() < self.p_abort:
            self.state = BeeState.RETURNING
        else:
            self.move_towards(self.resource_destination)

    def manage_death(self):
        """Handles tiny bee deaths."""
        if self.fed == 0:  # Death by starvation
            # print("Bee died by starvation")
            return self._remove_agent()

        """Handles death of BeeSwarm agent."""
        # Death by storm
        
        
        # Death by random outside risk
        if not self.is_in_hive and random() < self.p_death:
            return self._remove_agent()

    def _remove_agent(self):
        """Helper for removing agents."""
        self.model.n_agents_existed -= 1
        self.model.space.remove_agent(self)
        self.model.schedule.remove(self)
        self.model.agents.remove(self)
        self.remove()
